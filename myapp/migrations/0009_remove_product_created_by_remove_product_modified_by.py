# Generated by Django 4.2.4 on 2023-08-31 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_bought_created_at_bought_modified_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='product',
            name='modified_by',
        ),
    ]
