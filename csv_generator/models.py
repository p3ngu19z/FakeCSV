from django.core.validators import MinValueValidator
from django.db import models


class Schema(models.Model):
    title = models.CharField(max_length=128)
    last_update = models.DateTimeField()


class SchemaColumn(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=128)
    type = models.CharField(
        choices=(('fullname', 'Fullname'),
                 ('job', 'Job'),
                 ('email', 'Email'),
                 ('domain', 'Domain name'),
                 ('phone', 'Phone number'),
                 ('company', 'Company name'),
                 ('text', 'Text'),
                 ('integer', 'Integer'),
                 ('address', 'Address'),
                 ('date', 'Date')), max_length=64, blank=False)
    range_from = models.IntegerField(null=True, blank=True)
    range_to = models.IntegerField(null=True, blank=True)
    order = models.IntegerField(blank=True, validators=[MinValueValidator(0)])


class DataSet(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE)
    create_time = models.DateTimeField()
    status = models.BooleanField(default=0)
    filename = models.CharField(max_length=128, null=True)
