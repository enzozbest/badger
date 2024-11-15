from django.test import TestCase
from tutorials.models import User
from tutorials.models import KnowledgeArea

class KnowledgeAreaTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tutor", password="Password123")
        self.knowledge_area = KnowledgeArea.objects.create(user=self.user, subject='Python')

    def test_knowledge_area_str_method(self):
        expected_str = "Python"
        self.assertEqual(str(self.knowledge_area), expected_str)
