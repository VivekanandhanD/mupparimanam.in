# Generated by Django 3.1.3 on 2022-01-31 10:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobshistory',
            name='job_initiated_on',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
