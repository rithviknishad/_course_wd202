# Generated by Django 4.0.1 on 2022-02-17 16:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_taskstatuschangelogrecord'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TaskStatusChangeLogRecord',
            new_name='TaskStatusChangeLog',
        ),
    ]
