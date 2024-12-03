from django.forms.models import model_to_dict
from django.test import RequestFactory, TestCase
from django.urls import reverse

from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models import Request, Venue
from request_handler.views.show_all_requests import AllRequestsView
from user_system.fixtures.create_test_users import create_test_users
from user_system.models import User

INVALID_REQUEST_ID = 999


class viewRequestsTest(TestCase):
    def setUp(self):
        create_test_users()
        self.student = User.objects.get(user_type='Student')
        self.mode_preference = Venue.objects.create(venue="Online")

        self.client.force_login(self.student)

    # Tests that an unauthenticated user is redirected when attempting to view their lesson requests
    def test_redirect_if_not_logged_in_view_requests(self):
        self.client.logout()
        response = self.client.get(reverse('view_requests'))
        expected_url = f"{reverse('log_in')}?next={reverse('view_requests')}"
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)

    # Tests that a logged in user with requests can see them and the data is accurate
    def test_view_requests_populated(self):
        # Request instance belonging to test user
        self.request_instance = Request.objects.create(
            student=self.student,
            knowledge_area='C++',
            term='Easter',
            frequency='Weekly',
            duration='1h',
        )
        self.request_instance.venue_preference.set([self.mode_preference])

        response = self.client.get(reverse('view_requests'))
        self.assertTrue(response.context, {
            'Knowledge_area': 'C++',
            'Term': 'Easter',
            'Frequency': 'Weekly',
            'Duration': '1h',
            'Venue preference': 'Online',
            'Allocated': 'No',
            'Tutor': '-',
        })

    def test_tutor_view_request(self):
        tutor = User.objects.get(user_type='Tutor')
        self.client.force_login(tutor)
        self.request_instance = Request.objects.create(
            student=self.student,
            knowledge_area='C++',
            term='Easter',
            frequency='Weekly',
            duration='1h',
            tutor=tutor,
            allocated=True
        )
        self.request_instance.venue_preference.set([self.mode_preference])

        response = self.client.get(reverse('view_requests'))
        self.assertTrue(response.context, {
            'Knowledge_area': 'C++',
            'Term': 'Easter',
            'Frequency': 'Weekly',
            'Duration': '1h',
            'Venue preference': 'Online',
            'Allocated': 'Yes',
            'Tutor': self.request_instance.tutor_name,
        })

    def test_admin_view_request(self):
        admin = User.objects.get(user_type='Admin')
        self.client.force_login(admin)
        student_request = Request.objects.create(
            student=self.student,
            knowledge_area='C++',
            term='Easter',
            frequency='Weekly',
            duration='1h',
            allocated=False
        )
        tutor = User.objects.get(user_type='Tutor')
        tutor_request = Request.objects.create(
            student=self.student,
            knowledge_area='C++',
            term='Easter',
            frequency='Weekly',
            duration='1h',
            tutor=tutor,
            allocated=True
        )

        response = self.client.get(reverse('view_requests'))
        self.assertTrue(response.context, {model_to_dict(student_request).items().__hash__,
                                           model_to_dict(tutor_request).items().__hash__})

    # Tests that a logged in user who requests to view their requests (while having none) does not receive an error
    def test_view_requests_empty(self):
        response = self.client.get(reverse('view_requests'))
        self.assertEqual(list(response.context['requests']), [])

    def test_post_request_is_bad_request(self):
        response = self.client.post(reverse('view_requests'))
        self.assertEqual(response.status_code, 405)

    def test_unauthenticated_user_cannot_view_request(self):
        self.client.logout()
        response = self.client.get(reverse('view_requests'))
        expected_url = f"{reverse('log_in')}?next={reverse('view_requests')}"
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)

    def test_sort_by_id_ascending(self):
        request_1 = Request.objects.create(student=self.student, knowledge_area='C++', term='Easter')
        request_2 = Request.objects.create(student=self.student, knowledge_area='Databases', term='Fall')

        response = self.client.get(reverse('view_requests') + '?sort=id')

        self.assertQuerysetEqual(
            response.context['requests'],
            ['<Request: 1>', '<Request: 2>'],
            transform=lambda x: f'<Request: {x.id}>'
        )

    def test_sort_by_id_descending(self):
        request_1 = Request.objects.create(student=self.student, knowledge_area='C++', term='Easter')
        request_2 = Request.objects.create(student=self.student, knowledge_area='Databases', term='Fall')

        response = self.client.get(reverse('view_requests') + '?sort=-id')

        self.assertQuerysetEqual(
            response.context['requests'],
            ['<Request: 2>', '<Request: 1>'],
            transform=lambda x: f'<Request: {x.id}>'
        )

    def test_sort_by_knowledge_area_ascending(self):
        request_1 = Request.objects.create(student=self.student, knowledge_area='Databases', term='Fall')
        request_2 = Request.objects.create(student=self.student, knowledge_area='C++', term='Spring')

        response = self.client.get(reverse('view_requests') + '?sort=knowledge_area')

        self.assertQuerysetEqual(
            response.context['requests'],
            ['<Request: 2>', '<Request: 1>'],
            transform=lambda x: f'<Request: {x.id}>'
        )

    def test_sort_by_knowledge_area_descending(self):
        request_1 = Request.objects.create(student=self.student, knowledge_area='Databases', term='Fall')
        request_2 = Request.objects.create(student=self.student, knowledge_area='C++', term='Spring')

        response = self.client.get(reverse('view_requests') + '?sort=-knowledge_area')

        self.assertQuerysetEqual(
            response.context['requests'],
            ['<Request: 1>', '<Request: 2>'],
            transform=lambda x: f'<Request: {x.id}>'
        )

    def test_filter_by_allocation_status(self):
        create_test_requests()
        response = self.client.get(f'{reverse("view_requests")}?allocated=true')
        self.assertIsNotNone(response.context['requests'])
        self.assertQuerysetEqual(response.context['requests'], Request.objects.filter(allocated=True).all())

    def test_filter_by_search(self):
        create_test_requests()
        response = self.client.get(f'{reverse("view_requests")}?search=Charlie')
        self.assertIsNotNone(response.context['requests'])
        self.assertQuerysetEqual(response.context['requests'],
                                 Request.objects.filter(student=User.objects.get(user_type='Student')).all())

    def test_get_queryset_with_invalid_filterset(self):
        factory = RequestFactory()
        request = factory.get(reverse('view_requests'), {'invalid_filter': 'value'})
        request.user = self.student
        view = AllRequestsView()
        view.request = request
        view.setup(request)
        queryset = view.get_queryset()
        self.assertQuerysetEqual(queryset, Request.objects.all())
