from django.db import models

from user_system.models.user_model import User


class KnowledgeArea(models.Model):
    """Model to associate tutors to their knowledge areas."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_tutor': True})
    subject = models.CharField(max_length=30)

    def __str__(self):
        return self.subject
