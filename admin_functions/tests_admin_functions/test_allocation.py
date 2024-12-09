from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse
from request_handler.models import Request, Venue

from admin_functions.helpers import calculate_cost
from admin_functions.views.allocate_requests import get_suitable_tutors, get_venue_preference
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models import Request, Venue
from user_system.fixtures.create_test_users import create_test_users
from user_system.models import Day, User

class TestAllocation(TestCase):
    def setUp(self):
        create_test_users()
        create_test_requests()
        self.admin = User.objects.get(user_type=User.ACCOUNT_TYPE_ADMIN)
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.allocated_request = Request.objects.get(allocated=True)
        self.unallocated_request = Request.objects.get(allocated=False)
        self.online, _ = Venue.objects.get_or_create(venue='Online')
        self.tuesday = Day.objects.get(day='Tuesday')
        self.wednesday = Day.objects.get(day='Wednesday')

    def test_allocated_request_exists(self):
        self.assertIsNotNone(self.allocated_request)

    def test_unallocated_request_exists(self):
        self.assertIsNotNone(self.unallocated_request)

    def test_unauthenticated_user_cannot_see_page(self):
        response = self.client.get(reverse('allocate_request', args={self.unallocated_request.id}))
        self.assertRedirects(response,
                             f'{reverse("log_in")}?next={reverse("allocate_request", args={self.unallocated_request.id})}',
                             status_code=302, target_status_code=200)

    def test_student_cannot_allocate_requests_get(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed("permission_denied.html")

    def test_student_cannot_allocate_requests_post(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed("permission_denied.html")

    def test_tutors_cannot_allocate_requests_get(self):
        self.client.force_login(self.tutor)
        response = self.client.get(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed("permission_denied.html")

    def test_tutors_cannot_allocate_requests_post(self):
        self.client.force_login(self.tutor)
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed("permission_denied.html")

    def admin_can_send_get_request(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 200)

    def admin_can_send_post_request(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 200)

    def test_attempting_to_allocate_allocated_request_fails_get(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("allocate_request", args={self.allocated_request.id}))
        self.assertEqual(response.status_code, 409)
        self.assertTemplateUsed("already_allocated_error.html")

    def test_allocating_allocated_request_fails_post(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("allocate_request", args={self.allocated_request.id}))
        self.assertEqual(response.status_code, 409)
        self.assertTemplateUsed("already_allocated_error.html")

    def test_allocating_unallocated_request_works(self):
        response = self.allocate(self.tuesday.id, self.wednesday.id)
        self.unallocated_request.refresh_from_db()
        self.assertRedirects(response, reverse('view_requests'), status_code=302, target_status_code=200)
        self.assertTrue(self.unallocated_request.allocated)
        self.assertIsNotNone(self.unallocated_request.tutor)
        self.assertIsNotNone(self.unallocated_request.venue)
        self.assertIsNotNone(self.unallocated_request.day)
    
    #Not working
    def test_allocating_biweekly_request_works(self):
        #Create biweekly request with day = Tuesday and day2 = Wednesday
        Request.objects.all().delete()

        lesson_request = Request.objects.create(
            id=1,
            student=self.student,
            knowledge_area="Robotics",
            duration="1",
            term="May",
            frequency="Biweekly",
            allocated=False,
            tutor=None,
            is_recurring=False,
            late=False,
        )
        lesson_request.venue_preference.add(self.online.pk)
        lesson_request.save()
        self.unallocated_request = lesson_request
        self.unallocated_request.refresh_from_db()  
        response = self.allocate(self.tuesday.id, self.wednesday.id)
        print(Request.objects.all())
        self.unallocated_request.refresh_from_db()
        print(response.content)
        self.assertRedirects(response, reverse('view_requests'), status_code=302, target_status_code=200)
        self.assertTrue(self.unallocated_request.allocated)
        self.assertIsNotNone(self.unallocated_request.tutor)
        self.assertIsNotNone(self.unallocated_request.venue)
        self.assertIsNotNone(self.unallocated_request.day)

    #Not working
    '''
    def test_allocating_backwards_biweekly_request_works(self):
        #Create biweekly request with day = Wednesday and day2 = Tuesday
        lesson_request = Request.objects.create(
            id=10,
            allocated=False,
            tutor=self.tutor,
            student=self.student,
            term="September",
            day=self.wednesday,
            day2=self.tuesday,
            frequency="Biweekly",
            duration=60,
            is_recurring=False,
            knowledge_area="Robotics",
            venue=self.online,
        )
        self.unallocated_request = lesson_request
        response = self.allocate(self.wednesday.id, self.tuesday.id)
        print(response.content)
        self.unallocated_request.refresh_from_db()
        #self.assertRedirects(response, reverse('view_requests'), status_code=302, target_status_code=200)
        self.assertTrue(self.unallocated_request.allocated)
        self.assertIsNotNone(self.unallocated_request.tutor)
        self.assertIsNotNone(self.unallocated_request.venue)
        self.assertIsNotNone(self.unallocated_request.day)'''

    def test_invalid_allocation_reloads_form(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}), data={
            'tutor': 'AAAAAAAAAAA',
            'day1': '10'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("allocate_request.html")

    def test_get_method_unallocated_request(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("allocate_request.html")
    
    def test_basic_allocation_cost(self):
        self.allocate(self.tuesday.id, self.wednesday.id)
        tutor = get_object_or_404(User, id=self.tutor.id)
        cost = calculate_cost.calculate_cost(tutor, self.allocated_request.id)
        self.assertEqual(cost, 375.0)

    def test_recurring_allocation_cost(self):
        self.unallocated_request.is_recurring = True
        self.unallocated_request.save()
        self.allocate(self.tuesday.id, self.wednesday.id)
        self.unallocated_request.refresh_from_db()
        tutor = get_object_or_404(User, id=self.tutor.id)
        cost = calculate_cost.calculate_cost(tutor, self.allocated_request.id)
        self.assertEqual(cost, 375.0)

    def test_2hr30_session_cost(self):
        self.set_request_duration('2.5h')
        self.allocate(self.tuesday.id, self.wednesday.id)
        self.unallocated_request.refresh_from_db()
        tutor = get_object_or_404(User, id=self.tutor.id)
        cost = calculate_cost.calculate_cost(tutor, self.unallocated_request.id)
        self.assertEqual(cost, 937.5)

    def test_biweekly_allocation_cost(self):
        self.set_request_frequency("Biweekly")
        self.unallocated_request.day2 = self.wednesday
        self.allocate(self.tuesday.id, self.wednesday.id)
        self.unallocated_request.refresh_from_db()
        tutor = get_object_or_404(User, id=self.tutor.id)
        cost = calculate_cost.calculate_cost(tutor, self.unallocated_request.id)
        self.assertEqual(cost, 750.0)

    def test_fortnightly_allocation_cost(self):
        # Specifc test request that has a fortnightly lesson
        self.set_request_frequency("Fortnightly")
        self.allocate(self.tuesday.id, self.wednesday.id)

        self.unallocated_request.refresh_from_db()
        tutor = get_object_or_404(User, id=self.tutor.id)
        cost = calculate_cost.calculate_cost(tutor, self.unallocated_request.id)
        self.assertEqual(cost, 175.0)

    def test_any_other_frequency_is_invalid_returns_negative_cost(self):
        self.set_request_frequency()
        self.allocate(self.tuesday.id, self.wednesday.id)
        self.unallocated_request.refresh_from_db()
        tutor = get_object_or_404(User, id=self.tutor.id)
        cost = calculate_cost.calculate_cost(tutor, self.unallocated_request.id)
        self.assertTrue(cost <= 0)

    def test_first_get_method_displays_correct_form(self):
        self.client.force_login(self.admin)
        self.unallocated_request.frequency = 'Biweekly'
        response = self.client.get(reverse('allocate_request', args={self.unallocated_request.id}))
        self.assertTemplateUsed('allocate_request.html')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['form'].fields['tutor'].queryset, [])

    def test_post_request_missing_day1(self):
        self.client.force_login(self.admin)
        self.unallocated_request.frequency = 'Weekly'
        self.unallocated_request.save()
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}),
                                    data={'tutor': self.tutor.id,
                                          'venue': self.online.id
                                          })
        self.assertContains(response, "Missing required day1", status_code=400)
        self.assertEqual(response.status_code, 400)

    def test_biweekly_request_missing_day2(self):
        self.set_request_frequency('Biweekly')
        self.client.force_login(self.admin)
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}),
                                    data={'tutor': self.tutor.id,
                                          'venue': self.online.id,
                                          'day1': self.tuesday.id,
                                          })
        self.assertContains(response, "Missing required day2", status_code=400)
        self.assertEqual(response.status_code, 400)

    def test_post_form_without_tutor(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}),
                                    data={'day1': self.tuesday.id,
                                          })
        self.assertContains(response, "Missing required tutor", status_code=400)
        self.assertEqual(response.status_code, 400)

    def test_post_form_without_venue(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}),
                                    data={'day1': self.tuesday.id,
                                          'tutor': self.tutor.id,
                                          })
        self.assertContains(response, "Missing required venue", status_code=400)
        self.assertEqual(response.status_code, 400)

    def test_get_method_with_valid_parameters_results_in_a_form_with_tutors(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("allocate_request", args={self.unallocated_request.id}), data={
            'day1': self.tuesday.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("allocate_request.html")
        self.assertTrue(response.context['form'].fields['tutor'].queryset.count(), 1)

    def test_get_venue_preferences_works_with_no_preference(self):
        queryset = Venue.objects.all()
        result = get_venue_preference(queryset)
        self.assertQuerysetEqual(result.order_by('id'), Venue.objects.exclude(venue='No Preference').order_by('id'))

    def test_get_suitable_tutors_without_day1(self):
        result = get_suitable_tutors(self.unallocated_request.id, None, None)
        self.assertQuerysetEqual(result, [])

    def test_get_suitable_tutors_without_day2_biweekly(self):
        self.set_request_frequency('Biweekly')
        result = get_suitable_tutors(self.unallocated_request.id, self.tuesday.id, None)
        self.assertQuerysetEqual(result, [])

    def test_get_suitable_tutors_raises_404_if_invalid_request_id(self):
        self.assertRaises(Http404, get_suitable_tutors, -99, self.tuesday.id, self.wednesday.id)

    def set_request_frequency(self, frequency: str = ''):
        self.unallocated_request.frequency = frequency
        self.unallocated_request.save()

    def set_request_duration(self, duration: str = ''):
        self.unallocated_request.duration = duration
        self.unallocated_request.save()

    def allocate(self,day1,day2) -> HttpResponse:
        self.unallocated_request.refresh_from_db()
        self.client.force_login(self.admin)
        return self.client.post(reverse("allocate_request", args={self.unallocated_request.id}), data={
            'tutor': self.tutor.id,
            'venue': str(self.online.id),
            'day1': day1,
            'day2': day2,
        })
