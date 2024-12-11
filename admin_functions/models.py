from django.db import models


class DummyModel(models.Model):
    """Class representing a dummy model to be used in testing"""
    name = models.CharField(max_length=100)
    age = models.IntegerField()
