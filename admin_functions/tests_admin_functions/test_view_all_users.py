from django.test import TestCase
from django.urls import reverse
from user_system.models import User

class ViewAllUsersTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='Password123', user_type='Admin')
        for i in range(51):
            User.objects.create(username='@user{}'.format(i), password='Password123', email='user{}@test.com'.format(i),
                                user_type= 'Student' if i % 2 == 0 else 'Tutor')

    def test_post_request_not_allowed(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.post(reverse('view_all_users'))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'Method Not Allowed')

    def test_unauthenticated_user_cannot_send_request(self):
        response = self.client.get(reverse('view_all_users'), follow=True)
        self.assertRedirects(response, reverse('log_in'), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_student_cannot_send_request(self):
        student = User.objects.create_user(username='testuser2', email='test2@test.com', password='Password123', user_type='Student')
        self.client.login(username='testuser2', password='Password123')
        response = self.client.get(reverse('view_all_users'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_tutor_cannot_send_request(self):
        tutor = User.objects.create_user(username='testuser2', email='test2@test.com', password='Password123',
                                           user_type='Tutor')
        self.client.login(username='testuser2', password='Password123')
        response = self.client.get(reverse('view_all_users'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_admin_can_send_request(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(reverse('view_all_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_users.html')

    def test_pagination_works_correctly(self):
        self.client.login(username='testuser', password='Password123')

        #Use loop to check that navigation between pages will work correctly (in this case, pages 1 and 2 each have
        #20 users).
        for i in range(1, 3):
            response = self.client.get(reverse('view_all_users') + f'?page={i}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['page_obj']), 20)

        self.assertTemplateUsed(response, 'view_users.html')

    def test_paginator_works_correctly(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(reverse('view_all_users'))
        paginator = response.context['page_obj'].paginator
        self.assertEqual(paginator.num_pages, 3)

    def test_filter_by_user_type(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(reverse('view_all_users') + '?user_type=Student')
        self.assertEqual(response.status_code, 200)
        filtered_users = response.context['page_obj'].object_list
        self.assertTrue(all(user.user_type == 'Student' for user in filtered_users))

    def test_filter_and_paginate_combination(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(reverse('view_all_users') + '?user_type=Student&page=1')
        self.assertEqual(response.status_code, 200)
        filtered_users = response.context['page_obj'].object_list
        self.assertTrue(all(user.user_type == 'Student' for user in filtered_users))
        self.assertEqual(len(filtered_users), 20)

    def test_page_out_of_range_redirects_to_last_page(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(reverse('view_all_users') + '?page=999')
        self.assertEqual(response.status_code, 200)
        paginator = response.context['page_obj'].paginator
        self.assertEqual(response.context['page_obj'].number, paginator.num_pages)

    def test_filter_no_results_shows_all_users(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(reverse('view_all_users') + '?user_type=NA')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 52)

class SearchUsersTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='adminuser', email='admin@test.com', password='Password123', user_type='Admin')
        self.users = [
            User.objects.create(first_name="Alice", last_name="Anderson", username="alice", email="alice@test.com", user_type='Student'),
            User.objects.create(first_name="Bob", last_name="Brown", username="bob", email="bob@test.com", user_type='Student'),
            User.objects.create(first_name="Charlie", last_name="Chaplin", username="charlie", email="charlie@test.com", user_type='Tutor'),
        ]

    def test_search_by_first_name(self):
        self.client.login(username='adminuser', password='Password123')
        response = self.client.get(reverse('view_all_users') + '?q=Alice')
        self.assertEqual(response.status_code, 200)
        search_results = response.context['page_obj'].object_list
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].first_name, 'Alice')

    def test_search_by_last_name(self):
        self.client.login(username='adminuser', password='Password123')
        response = self.client.get(reverse('view_all_users') + '?q=Brown')
        self.assertEqual(response.status_code, 200)
        search_results = response.context['page_obj'].object_list
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].last_name, 'Brown')

    def test_search_with_user_that_does_not_exist(self):
        self.client.login(username='adminuser', password='Password123')
        response = self.client.get(reverse('view_all_users') + '?q=David')
        self.assertEqual(response.status_code, 200)
        search_results = response.context['page_obj'].object_list
        self.assertEqual(len(search_results), 0)

    def test_search_combined_with_filter(self):
        self.client.login(username='adminuser', password='Password123')
        response = self.client.get(reverse('view_all_users') + '?user_type=Student&q=Alice') #?q=Alice&page=2'
        self.assertEqual(response.status_code, 200)
        search_results = response.context['page_obj'].object_list
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].first_name, 'Alice')
        self.assertEqual(search_results[0].user_type, 'Student')

    def test_search_case_insensitivity(self):
        self.client.login(username='adminuser', password='Password123')
        response = self.client.get(reverse('view_all_users') + '?q=aLiCe')
        self.assertEqual(response.status_code, 200)
        search_results = response.context['page_obj'].object_list
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].first_name, 'Alice')

    def test_search_by_full_name(self):
        self.client.login(username='adminuser', password='Password123')
        response = self.client.get(reverse('view_all_users'), {'q': 'Alice Anderson'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Anderson')
        self.assertNotContains(response, 'Bob Brown')