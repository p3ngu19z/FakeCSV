import datetime

from django import forms
from .models import Schema, SchemaColumn


class SchemaForm(forms.ModelForm):
    class Meta:
        model = Schema
        fields = ['title']


class SchemaColumnForm(forms.ModelForm):
    class Meta:
        model = SchemaColumn
        fields = ['name', 'type', 'range_from', 'range_to', 'order']


class DataSetForm(forms.Form):
    rows = forms.IntegerField(max_value=1000)
