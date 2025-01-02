# api/models.py
from django.db import models

# Create your models here.


class Token(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    user_id = models.IntegerField()
    is_used = models.BooleanField(default=False)


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=False)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=10, null=True)
    country = models.CharField(max_length=63, null=True)
    admin = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
