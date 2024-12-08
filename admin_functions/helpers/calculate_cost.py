from django.shortcuts import get_object_or_404

from request_handler.models import Request, User


def calculate_cost(tutor: User, request_id: int) -> float:
    """Calculates the cost for an invoice to be sent to a student

    Assumes 15-week terms.
    If students have selected to have recurring sessions, the admins must generate a new invoice before the start
    of each term. calculate_cost only generates the cost for a single term.
    :param tutor: the Tutor user for the invoice
    :param request_id: the id of the tutoring request object
    :return: the cost for the invoice as a float.
    """

    lesson_request = get_object_or_404(Request, id=request_id)
    duration = lesson_request.duration
    frequency = lesson_request.frequency
    lesson_num = calculate_num_lessons(frequency)
    cost = float(tutor.hourly_rate) * float(duration[:-1]) * lesson_num
    return cost


def calculate_num_lessons(frequency: str) -> int:
    """Calculates the number of lessons for a specific frequency.
    
    :param frequency: the frequency of lessons, as specified in the tutoring request.
    :return: an integer representing the number of lessons for the tutoring request.
    """
    match frequency:
        case "Weekly":
            return 15
        case "Biweekly":
            return 30
        case "Fortnightly":
            return 7
        case _:
            return -1
