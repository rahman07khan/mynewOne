# Generated by Django 4.2.4 on 2023-09-01 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_remove_masterrole_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterrole',
            name='created_by',
            field=models.CharField(editable=False, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='masterrole',
            name='modified_by',
            field=models.CharField(editable=False, max_length=255, null=True),
        ),
    ]
