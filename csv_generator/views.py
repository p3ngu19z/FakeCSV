import datetime
import boto3

from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import SchemaForm, SchemaColumnForm, DataSetForm
from .models import Schema, SchemaColumn, DataSet
from .tasks import generate_fake_csv


@login_required
def schemas(request):
    all_schemas = Schema.objects.all()
    return render(request, 'csv_generator/schemas.html', {'schemas': all_schemas})


@login_required
def new_schema(request):
    if request.method == 'POST':
        schema_form = SchemaForm(request.POST)
        if schema_form.is_valid():
            schema = schema_form.save(commit=False)
            schema.last_update = datetime.datetime.now()
            schema.save()
            return redirect('edit_schema', pk=schema.id)
    else:
        schema_form = SchemaForm()
    return render(request, 'csv_generator/new_schema.html', {'schema_form': schema_form})


@login_required
def edit_schema(request, pk):
    current_schema = Schema.objects.get(id=pk)
    current_columns = current_schema.columns.order_by('order').all()
    schema_column_form = SchemaColumnForm()
    if request.method == 'POST':
        schema_form = SchemaForm(request.POST)
        if schema_form.is_valid():
            current_schema.title = schema_form.cleaned_data['title']
            current_schema.last_update = datetime.datetime.now()
            current_schema.save()
    else:
        schema_form = SchemaForm()
    return render(request, 'csv_generator/edit_schema.html',
                  {'current_schema': current_schema, 'current_columns': current_columns, 'schema_form': schema_form,
                   'schema_column_form': schema_column_form})


@login_required
def add_schema_column(request, schema_pk):
    current_schema = Schema.objects.get(id=schema_pk)
    current_columns = current_schema.columns.order_by('order').all()
    schema_form = SchemaForm()
    if request.method == 'POST':
        schema_column_form = SchemaColumnForm(request.POST)
        if schema_column_form.is_valid():
            schema_column = schema_column_form.save(commit=False)
            schema_column.schema = current_schema
            last_column = SchemaColumn.objects.filter(schema_id=current_schema.pk).order_by('order').last() or None
            if not last_column:
                schema_column.order = 0
            else:
                if type(schema_column.order) is int:
                    if schema_column.order > last_column.order:
                        schema_column.order = last_column.order + 1
                    else:
                        SchemaColumn.objects.filter(schema_id=current_schema.pk) \
                            .filter(order__gte=schema_column.order).update(order=F('order') + 1)
                else:
                    schema_column.order = 0 if not last_column else last_column.order + 1
            schema_column.save()
    else:
        schema_column_form = SchemaColumnForm()
    return render(request, 'csv_generator/edit_schema.html',
                  {'current_schema': current_schema, 'current_columns': current_columns, 'schema_form': schema_form,
                   'schema_column_form': schema_column_form})


@login_required
def delete_schema(request, pk):
    Schema.objects.get(id=pk).delete()
    return redirect('schemas')


@login_required
def delete_schema_column(request, schema_pk, column_pk):
    current_schema_column = SchemaColumn.objects.get(id=column_pk)
    SchemaColumn.objects.filter(schema_id=schema_pk) \
        .filter(order__gte=current_schema_column.order).update(order=F('order') - 1)
    current_schema_column.delete()
    return redirect('edit_schema', pk=schema_pk)


@login_required
def data_sets(request, schema_pk):
    current_schema = Schema.objects.get(id=schema_pk)
    current_data_sets = DataSet.objects.filter(schema_id=schema_pk).all()
    data_set_form = DataSetForm()
    return render(request, 'csv_generator/datasets.html',
                  {'current_schema': current_schema, 'current_data_sets': current_data_sets,
                   'data_set_form': data_set_form})


@login_required
def generate_data_set(request, schema_pk):
    current_schema = Schema.objects.get(id=schema_pk)
    if request.method == 'POST':
        data_set_form = DataSetForm(request.POST)
        if data_set_form.is_valid():
            rows = int(data_set_form.cleaned_data['rows'])
            new_data_set = DataSet(schema=current_schema, create_time=datetime.datetime.now())
            new_data_set.save()
            generate_fake_csv.delay(schema_id=schema_pk, data_set_id=new_data_set.id, rows=rows)

    return redirect('data_sets', schema_pk=schema_pk)


def url_data_set(request, data_set_pk):
    client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          config=boto3.session.Config(signature_version=settings.AWS_S3_SIGNATURE_VERSION,
                                                      region_name=settings.AWS_S3_REGION_NAME))
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    data_set = DataSet.objects.get(id=data_set_pk)
    file_name = data_set.filename

    url = client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': file_name},
        ExpiresIn=600)
    return HttpResponseRedirect(url)
