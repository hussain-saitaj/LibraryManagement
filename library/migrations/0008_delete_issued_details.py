# Generated by Django 4.0.6 on 2022-07-20 09:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_issued_details'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Issued_details',
        ),
    ]