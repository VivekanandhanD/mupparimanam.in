import uuid

from django.conf import settings
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
    profile_pic = models.FileField(upload_to='uploads/%Y/%m/%d/', blank=True)
    mobile_no = PhoneNumberField()
    # address = models.ForeignKey(Address, on_delete=models.CASCADE)


class RenderHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    render_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rendered_on = models.DateTimeField()


class Files(models.Model):
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")


class RenderFiles(models.Model):
    render = models.ForeignKey(RenderHistory, on_delete=models.CASCADE)
    files = models.ManyToManyField(Files)
