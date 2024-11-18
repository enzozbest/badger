from django.test import TestCase
from django.urls import reverse
from user_system.models import User
from user_system.models import KnowledgeArea

class DeleteKnowledgeAreaTest(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(username="testuser1", password="Password123", email="tutor1@outlook.com", user_type=User.ACCOUNT_TYPE_TUTOR)
        self.knowledge_area_1 = KnowledgeArea.objects.create(user=self.user_1, subject="Python")
        self.knowledge_area_2 = KnowledgeArea.objects.create(user=self.user_1, subject="Java")
        self.user_2 = User.objects.create_user(username="testuser2", password="Password123", email="tutor2@outlook.com", user_type=User.ACCOUNT_TYPE_TUTOR)

    # Tests that a tutor can delete a knowledge area successfully.
    def test_user_can_delete_knowledge_area(self):
        self.client.login(username="testuser1", password="Password123")
        self.assertTrue(KnowledgeArea.objects.filter(id=self.knowledge_area_1.id).exists())
        response = self.client.get(reverse('delete_knowledge_area', args=[self.knowledge_area_1.id]))
        self.assertFalse(KnowledgeArea.objects.filter(id=self.knowledge_area_1.id).exists())
        self.assertRedirects(response, reverse('add_knowledge_areas'))

    # Tests that one user cannot delete another users knowledge area
    def test_user_can_not_delete_others_knowledge_area(self):
        self.client.login(username="testuser1", password="Password123")
        self.assertTrue(KnowledgeArea.objects.filter(id=self.knowledge_area_2.id).exists())
        self.client.logout()
        self.client.login(username="testuser2", password="Password123")
        response = self.client.get(reverse('delete_knowledge_area', args=[self.knowledge_area_2.id]))
        self.assertTrue(KnowledgeArea.objects.filter(id=self.knowledge_area_2.id).exists())
        self.assertEqual(response.status_code, 404)

    # Tests that a user who is not logged in is redirected
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('delete_knowledge_area', args=[self.knowledge_area_1.id]))
        self.assertRedirects(response, '/log_in/?next=' + reverse('delete_knowledge_area', args=[self.knowledge_area_1.id]))

    # Tests that a non-tutor cannot delete a knowledge area
    def test_not_tutor_cannot_delete_knowledge_area(self):
        self.student = User.objects.create_user(username='studentuser', password='Password123', email="student@outlook.com", user_type=User.ACCOUNT_TYPE_STUDENT)
        self.client.login(username='studentuser', password='Password123')
        response = self.client.get(reverse('delete_knowledge_area', args=[self.knowledge_area_2.id]))
        self.assertEqual(response.status_code, 404)



