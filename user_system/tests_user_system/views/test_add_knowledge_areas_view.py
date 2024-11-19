from django.test import TestCase
from django.urls import reverse
from user_system.models import User
from user_system.models import KnowledgeArea

class AddKnowledgeAreasTest(TestCase):
    def setUp(self):
        # Create a tutor and a user who is not a tutor (student)
        self.tutor_user = User.objects.create_user(username='tutor', password='Password123',
                                                   email="tutor@example.com", user_type=User.ACCOUNT_TYPE_TUTOR)
        self.student_user = User.objects.create_user(username='student', password='Password123',
                                                     email="student@example.come", user_type=User.ACCOUNT_TYPE_STUDENT)
        KnowledgeArea.objects.create(user=self.tutor_user, subject='Python')
        KnowledgeArea.objects.create(user=self.student_user, subject='Java')
        self.url = reverse('add_knowledge_areas')

    # Tests that a non-tutor is redirected if they attempt to access the add knowledge areas page
    def test_redirect_non_tutor(self):
        self.client.login(username='student', password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('profile'))

    # Tests that the tutor can access the knowledge area page
    def test_tutor_can_access_knowledge_area_page(self):
        self.client.login(username='tutor', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_knowledge_areas.html')

    # Tests that a tutor should successfully be able to add a knowledge area
    def test_adding_knowledge_area(self):
        self.client.login(username='tutor', password='Password123')
        data = {'subject': 'Django'}
        response = self.client.post(self.url, data)

        self.assertEqual(KnowledgeArea.objects.count(), 3)  # Total of 3 subjects (2 from setUp)
        self.assertEqual(KnowledgeArea.objects.last().subject, 'Django')
        self.assertRedirects(response, self.url)

    # Tests that a tutor cannot add the same knowledge area again
    def test_prevent_duplicate_knowledge_area(self):
        self.client.login(username='tutor', password='Password123')
        data = {'subject': 'Python'}
        response = self.client.post(self.url, data)
        self.assertEqual(KnowledgeArea.objects.count(), 2)

    # Tests that the already added knowledge areas are passed and displayed correctly
    def test_existing_knowledge_areas_displayed_correctly(self):
        self.client.login(username='tutor', password='Password123')
        knowledge_areas = KnowledgeArea.objects.all()
        self.assertEqual(len(knowledge_areas), 2)
        self.assertEqual(knowledge_areas[0].subject, 'Python')
        self.assertEqual(knowledge_areas[1].subject, 'Java')


