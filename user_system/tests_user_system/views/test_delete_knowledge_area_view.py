from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from user_system.models import KnowledgeArea, User


class DeleteKnowledgeAreaTest(TestCase):
    def setUp(self):
        from user_system.fixtures import create_test_users
        create_test_users.create_test_users()

        self.tutor_user = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.tutor_areas = KnowledgeArea.objects.filter(user=self.tutor_user).all()
        self.knowledge_area_1 = self.tutor_areas.first()
        self.knowledge_area_2 = self.tutor_areas.last()

        self.user2 = User.objects.create_user(username='@testuser1', password='Password123',
                                              user_type=User.ACCOUNT_TYPE_TUTOR,
                                              email='test@example.org')

        KnowledgeArea.objects.create(user=self.user2, subject=self.knowledge_area_1.subject)

    # Tests that a tutor can delete a knowledge area successfully.
    def test_user_can_delete_knowledge_area(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        self.assertTrue(KnowledgeArea.objects.filter(id=self.knowledge_area_1.id).exists())
        response = self.client.get(reverse('delete_knowledge_area', args=[self.knowledge_area_1.id]))
        self.assertFalse(KnowledgeArea.objects.filter(id=self.knowledge_area_1.id).exists())
        self.assertRedirects(response, reverse('add_knowledge_areas'))

    # Tests that one user cannot delete another users' knowledge areas
    def test_user_can_not_delete_others_knowledge_area(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        self.assertTrue(KnowledgeArea.objects.filter(id=self.knowledge_area_2.id).exists())
        self.client.logout()
        self.client.login(username=self.user2.username, password='Password123')
        response = self.client.get(reverse('delete_knowledge_area', args=[self.knowledge_area_2.pk]))
        self.assertTrue(KnowledgeArea.objects.filter(id=self.knowledge_area_2.id).exists())
        self.assertEqual(response.status_code, 404)

    # Tests that a user who is not logged in is redirected
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('delete_knowledge_area', args=[self.knowledge_area_1.id]))
        self.assertRedirects(response,
                             '/log_in/?next=' + reverse('delete_knowledge_area', args=[self.knowledge_area_1.id]))

    # Tests that a non-tutor cannot delete a knowledge area
    def test_not_tutor_cannot_delete_knowledge_area(self):
        student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.client.login(username=student.username, password='Password123')
        response = self.client.get(reverse('delete_knowledge_area', args=[self.knowledge_area_2.id]))
        self.assertRaises(Http404)
        self.assertEqual(response.status_code, 404)
