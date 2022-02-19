# Generated by Django 4.0.1 on 2022-02-19 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_userreportconfiguration'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreportconfiguration',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='userreportconfiguration',
            name='dispatch_time',
            field=models.TimeField(auto_now=True),
        ),
    ]
