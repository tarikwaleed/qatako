from django.db import models


class CommandException(models.Model):
    time = models.DateTimeField(auto_now=True)
    command = models.CharField(max_length=50, default="")
    count = models.IntegerField()

class Feedings(models.Model):
    app=models.CharField(max_length=50)
    feeder=models.CharField(max_length=50)
    last_fed=models.DateTimeField(auto_now=True,blank=False,editable=True)
