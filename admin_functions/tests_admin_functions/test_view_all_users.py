from django.test import RequestFactory, TestCase
from django.urls import reverse

from admin_functions.helpers.filters import UserFilter
from admin_functions.views.view_all_users import AllUsersView
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.user_model import User

class ViewAllUsersTestCase(TestCase):
    def setUp(self):
        create_test_users()
        self.user = User.objects.get(user_type='Admin')
        self.student = User.objects.get(user_type='Student')
        for i in range(51):
            User.objects.create(username='@user{}'.format(i), password='Password123', email='user{}@test.com'.format(i),
                                user_type='Student' if i % 2 == 0 else 'Tutor')

    def tearDown(self):
        if not hasattr(AllUsersView, 'filterset_class'):
            setattr(AllUsersView, 'filterset_class', UserFilter)
        super().tearDown()

    def test_post_request_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('view_all_users'))
        self.assertEqual(response.status_code, 405)

    def test_unauthenticated_user_cannot_send_request(self):
        response = self.client.get(reverse('view_all_users'), follow=True)
        expected_url = f'{reverse("log_in")}?next={reverse("view_all_users")}'
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_student_cannot_send_request(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('view_all_users'))
        self.assertEqual(response.status_code, 403)

    def test_tutor_cannot_send_request(self):
        self.client.force_login(User.objects.filter(user_type='Tutor').all()[0])
        response = self.client.get(reverse('view_all_users'))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_send_request(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_users.html')

    def test_pagination_works_correctly(self):
        self.client.force_login(self.user)
        # Use loop to check that navigation between pages will work correctly (in this case, pages 1 and 2 each have
        # 20 users).
        for i in range(1, 3):
            response = self.client.get(reverse('view_all_users') + f'?page={i}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['page_obj']), 20)

        self.assertTemplateUsed(response, 'view_users.html')

    def test_paginator_works_correctly(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users'))
        paginator = response.context['page_obj'].paginator
        self.assertEqual(paginator.num_pages, 3)

    def test_filter_by_user_type(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?user_type=Student')
        self.assertEqual(response.status_code, 200)
        filtered_users = response.context['page_obj'].object_list
        self.assertTrue(all(user.user_type == 'Student' for user in filtered_users))

    def test_filter_and_paginate_combination(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?user_type=Student&page=1')
        self.assertEqual(response.status_code, 200)
        filtered_users = response.context['page_obj'].object_list
        self.assertTrue(all(user.user_type == 'Student' for user in filtered_users))
        self.assertEqual(len(filtered_users), 20)

    def test_page_out_of_range_redirects_to_last_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?page=999', follow=True)
        paginator = response.context['page_obj'].paginator
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, paginator.num_pages)

    def test_filter_no_results_shows_all_users(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?user_type=NA')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 54)

    def test_get_queryset_without_filterset_class(self):
        if hasattr(AllUsersView, 'filterset_class'):
            delattr(AllUsersView, 'filterset_class')
        factory = RequestFactory()
        request = factory.get('/some-url')
        request.user = self.user
        view = AllUsersView()
        view.request = request
        view.setup(request)
        queryset = view.get_queryset()
        self.assertEqual(len(queryset), User.objects.count())


class SearchUsersTestCase(TestCase):
    def setUp(self):
        create_test_users()
        self.user = User.objects.get(user_type='Admin')
        self.users = [
            User.objects.create(first_name="Alice", last_name="Anderson", username="alice", email="alice@test.com",
                                user_type='Student'),
            User.objects.create(first_name="Bob", last_name="Brown", username="bob", email="bob@test.com",
                                user_type='Student'),
            User.objects.create(first_name="Charlie", last_name="Chaplin", username="charlie", email="charlie@test.com",
                                user_type='Tutor'),
        ]

    def test_search_by_first_name(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?search=Alice')
        self.assertEqual(response.status_code, 200)
        search_results = response.context['page_obj'].object_list
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].first_name, 'Alice')

    def test_search_by_last_name(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?search=Brown')
        self.assertEqual(response.status_code, 200)
        search_results = response.context['page_obj'].object_list
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].last_name, 'Brown')

    def test_search_with_user_that_does_not_exist(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?search=David')
        self.assertEqual(response.status_code, 200)
        search_results = response.context['page_obj'].object_list
        self.assertEqual(len(search_results), 0)

    def test_search_combined_with_filter(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?user_type=Student&search=Alice')  # ?q=Alice&page=2'
        self.assertEqual(response.status_code, 200)
        search_results = response.context['page_obj'].object_list
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].first_name, 'Alice')
        self.assertEqual(search_results[0].user_type, 'Student')

    def test_search_case_insensitivity(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?search=aLiCe')
        self.assertEqual(response.status_code, 200)
        search_results = response.context['page_obj'].object_list
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].first_name, 'Alice')

    def test_search_by_full_name(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users'), {'search': 'Alice Anderson'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Anderson')
        self.assertNotContains(response, 'Bob Brown')


class ViewAllUsersSortingTestCase(TestCase):
    def setUp(self):
        create_test_users()
        self.user = User.objects.get(user_type='Admin')
        self.users = [
            User.objects.create(
                username=f'user{i}',
                first_name=f'First{i}',
                last_name=f'Last{i}',
                email=f'{chr(97 + i)}@test.com',
                user_type='Student' if i % 2 == 0 else 'Tutor'
            ) for i in range(5)
        ]

    def test_sort_by_email(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?sort=email')
        emails = [user.email for user in response.context['users']]
        self.assertEqual(emails, sorted(emails))

    def test_sort_by_email_descending(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?sort=-email')
        emails = [user.email for user in response.context['users']]
        self.assertEqual(emails, sorted(emails, reverse=True))

    def test_sort_by_first_name(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?sort=first_name')
        first_names = [user.first_name for user in response.context['users']]
        self.assertEqual(first_names, sorted(first_names))

    def test_sort_by_first_name_descending(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?sort=-first_name')
        first_names = [user.first_name for user in response.context['users']]
        self.assertEqual(first_names, sorted(first_names, reverse=True))

    def test_sort_by_last_name(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?sort=last_name')
        last_names = [user.last_name for user in response.context['users']]
        self.assertEqual(last_names, sorted(last_names))

    def test_sort_by_last_name_descending(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?sort=-last_name')
        last_names = [user.last_name for user in response.context['users']]
        self.assertEqual(last_names, sorted(last_names, reverse=True))

    def test_sort_by_user_type(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?sort=user_type')
        user_types = [user.user_type for user in response.context['users']]
        self.assertEqual(user_types, sorted(user_types))

    def test_sort_by_user_type_descending(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_all_users') + '?sort=-user_type')
        user_types = [user.user_type for user in response.context['users']]
        self.assertEqual(user_types, sorted(user_types, reverse=True))
