# Generated by Django 4.2.4 on 2023-09-01 05:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_rename_created_by_id_masterrole_created_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='masterrole',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='masterrole',
            name='modified_by',
        ),
    ]