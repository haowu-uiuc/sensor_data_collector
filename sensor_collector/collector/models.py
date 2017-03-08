from __future__ import unicode_literals

from django.db import models


# Create your models here.
# class User(models.Model):
#     user_name = models.CharField(max_length=200)


class AudioRecord(models.Model):
    user_name = models.CharField(max_length=200)
    timestamp = models.BigIntegerField()
    fft_vector = models.TextField()
    td_vector = models.TextField()
