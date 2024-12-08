from django import forms

from user_system.models.knowledge_area_model import KnowledgeArea


def get_knowledge_areas():
    """Function to get all knowledge areas available in our platform

    :return: list of Knowledge Areas
    """
    return [
        ('C++', 'C++'),
        ('Scala', 'Scala'),
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('Django', 'Django'),
        ('JavaScript', 'JavaScript'),
        ('Databases', 'Databases'),
        ('Robotics', 'Robotics'),
        ('Internet Systems', 'Internet Systems'),
    ]


class KnowledgeAreaForm(forms.ModelForm):
    """Form to set knowledge areas."""

    class Meta:
        model = KnowledgeArea
        fields = ['subject']

    subject = forms.ChoiceField(choices=get_knowledge_areas())
