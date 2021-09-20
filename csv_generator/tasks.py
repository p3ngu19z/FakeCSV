import csv
import random
import uuid

from celery import shared_task
from django.core.files.storage import default_storage
from faker import Faker

from .models import Schema, DataSet


def generate_fake(name, range_from=None, range_to=None):
    fake = Faker()
    if name == 'fullname':
        return fake.name()
    elif name == 'job':
        return fake.job()
    elif name == 'email':
        return fake.email()
    elif name == 'domain':
        return fake.domain_name()
    elif name == 'phone':
        return fake.phone_number()
    elif name == 'company':
        return fake.company()
    elif name == 'text':
        try:
            return ' '.join([fake.sentence() for i in range(random.randint(range_from, range_to))])
        except:
            return fake.text()
    elif name == 'integer':
        try:
            return fake.pyint(min_value=range_from, max_value=range_to)
        except:
            return fake.pyint()
    elif name == 'address':
        return fake.address()
    elif name == 'date':
        return fake.date()


@shared_task(bind=True)
def generate_fake_csv(self, schema_id, data_set_id, rows):
    current_dataset = DataSet.objects.get(id=data_set_id)
    current_schema = Schema.objects.get(id=schema_id)
    current_schema_columns = current_schema.columns.order_by('order').all()
    current_dataset.status = True
    filename = str(uuid.uuid4()) + '.csv'
    current_dataset.filename = filename

    with default_storage.open(filename, 'wt') as csv_fake:
        cvs_writer = csv.writer(csv_fake)
        cvs_writer.writerow([i.name for i in current_schema_columns])
        for x in range(rows):
            cvs_writer.writerow(
                [generate_fake(x.type, range_from=x.range_from, range_to=x.range_to) for x in
                 current_schema_columns])

    current_dataset.save()
