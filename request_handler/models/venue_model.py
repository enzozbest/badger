from django.db import models


class Venue(models.Model):
    """ Class representing a venue for tutoring sessions.

    This Model is necessary for the ManyToMany relationships in Request to work, as they must be between model instances.
    Modes are represented in the database as a string (In person, Online, No preference) and an automatically assigned id (primary key).
    """
    venue = models.CharField(max_length=10)

    def __str__(self):
        return self.venue
