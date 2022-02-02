# Generated by Django 3.1.3 on 2022-02-02 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20220131_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files',
            name='file',
            field=models.FileField(default='', upload_to='web/static/uploads/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_pic',
            field=models.FileField(blank=True, upload_to='web/static/dp/%Y/%m/%d/'),
        ),
    ]
