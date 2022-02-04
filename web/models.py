import uuid
from datetime import datetime

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


# class Address(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     address_1 = models.CharField(max_length=128)
#     address_2 = models.CharField(max_length=128, blank=True)
#     city = models.CharField(max_length=64)
#     state = models.CharField(max_length=64)
#     zip_code = models.CharField(max_length=5)


class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.FileField(upload_to='web/static/dp/%Y/%m/%d/', blank=True)
    mobile_no = PhoneNumberField()
    # address = models.ForeignKey(Address, on_delete=models.CASCADE)


class JobsHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initiated_on = models.DateTimeField(default=datetime.now, blank=False)
    obj_file = models.FileField(upload_to="web/static/outputs/%Y/%m/%d/", blank=False, default='')
    complete_status = models.IntegerField(default=0)
    completed_on = models.DateTimeField(default=datetime.now, blank=True)
    remove_status = models.IntegerField(default=0)


class Files(models.Model):
    file = models.FileField(upload_to="web/static/uploads/%Y/%m/%d/", default='', blank=False,
                            validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])


class JobFiles(models.Model):
    job_file = models.AutoField(primary_key=True)
    job = models.ForeignKey(JobsHistory, on_delete=models.CASCADE)
    files = models.ForeignKey(Files, on_delete=models.CASCADE, default='', blank=False)
