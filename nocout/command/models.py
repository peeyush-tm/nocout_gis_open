from django.db import models

class Command(models.Model):
    command_name = models.CharField(max_length=100)
    command_line = models.CharField(max_length=100)
    