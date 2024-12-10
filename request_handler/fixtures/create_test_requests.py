import json

from request_handler.models import Request, Venue
from user_system.models.user_model import User
from user_system.models.day_model import Day


def create_test_requests():
    """Function to create the requests set in the fixture test_requests.json

    This function parses the JSON file and, for each fixed request, generates a corresponding Request model object so that
    the requests are available in the database.
    This code has deliberately not been refactored to keep this loader simple: should any changes need to be made to the
    fixtures, you will always need only alter the JSON fixture. This code should never be changed.
    """

    with open('request_handler/fixtures/test_requests.json', 'r') as file:
        requests_json = json.load(file)

        for request_json in requests_json:
            venue_pref = request_json.pop('venue_preference', [])

            student_json = request_json.pop('student', [])
            try:
                student = User.objects.get(first_name=student_json)
                request_json['student'] = student
            except User.DoesNotExist:
                print("User not found!")

            if request_json['allocated']:
                tutor_name = request_json.pop('tutor', None)
                first_name, last_name = tutor_name.split()
                try:
                    tutor = User.objects.get(first_name=first_name, last_name=last_name)
                    request_json['tutor'] = tutor
                except User.DoesNotExist:
                    print("Tutor not found!")
                day_name = request_json.pop('day', [])
                venue_name = request_json.pop('venue', [])
                venue = Venue.objects.filter(venue=venue_name).all()[0]
                day = Day.objects.get(day=day_name)
                request_json['day'] = day
                request_json['venue'] = venue
                request, _ = Request.objects.get_or_create(**request_json)
            else:
                request, _ = Request.objects.get_or_create(**request_json)
                if venue_pref:
                    request.venue_preference.add(Venue.objects.filter(venue=venue_pref).all()[0])
                else:
                    request.venue_preference.add(Venue.objects.filter(venue="No Preference").all()[0])
