# Generated by Django 4.2.4 on 2023-09-01 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0021_masterrole_created_by_masterrole_modified_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='masterrole',
            name='modified_by',
        ),
        migrations.AlterField(
            model_name='masterrole',
            name='created_by',
            field=models.IntegerField(editable=False, null=True),
        ),
    ]
