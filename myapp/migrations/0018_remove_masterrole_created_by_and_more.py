# Generated by Django 4.2.4 on 2023-09-01 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_alter_masterrole_created_by_and_more'),
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
        migrations.AddField(
            model_name='masterrole',
            name='created_by_id',
            field=models.IntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='masterrole',
            name='modified_by_id',
            field=models.IntegerField(editable=False, null=True),
        ),
    ]
