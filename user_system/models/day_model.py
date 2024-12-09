from django.db import models


class Day(models.Model):
    """ Class representing a day of the week

    This Model is necessary for the ManyToMany relationships in Request to work, as they must be between model instances.
    Days are represented in the database as a string (their name) and an automatically assigned id (primary key).
    """

    day = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.day
