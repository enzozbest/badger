from django.test import TestCase
from django.urls import reverse

from user_system.models.knowledge_area_model import KnowledgeArea
from user_system.models.user_model import User


class AddKnowledgeAreasTest(TestCase):
    def setUp(self):
        from user_system.fixtures import create_test_users
        create_test_users.create_test_users()

        self.tutor_user = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.student_user = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)

        self.url = reverse('add_knowledge_areas')

    # Tests that a non-tutor is redirected if they attempt to access the add knowledge areas page
    def test_redirect_non_tutor(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('profile'))

    # Tests that the tutor can access the knowledge area page
    def test_tutor_can_access_knowledge_area_page(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_knowledge_areas.html')

    # Tests that a tutor should successfully be able to add a knowledge area
    def test_adding_knowledge_area(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        data = {'subject': 'Django'}
        response = self.client.post(self.url, data)

        self.assertEqual(KnowledgeArea.objects.count(), 4)  # Total of 4 subjects (3 from setUp)
        self.assertEqual(KnowledgeArea.objects.last().subject, 'Django')
        self.assertRedirects(response, self.url)

    # Tests that a tutor cannot add the same knowledge area again
    def test_prevent_duplicate_knowledge_area(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        data = {'subject': 'Python'}
        self.client.post(self.url, data)
        self.assertEqual(KnowledgeArea.objects.count(), 3)

    # Tests that the already added knowledge areas are passed and displayed correctly
    def test_existing_knowledge_areas_displayed_correctly(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        knowledge_areas = KnowledgeArea.objects.all()
        self.assertEqual(len(knowledge_areas), 3)
        self.assertEqual(knowledge_areas[0].subject, 'Python')
        self.assertEqual(knowledge_areas[1].subject, 'Scala')
        self.assertEqual(knowledge_areas[2].subject, 'Java')
