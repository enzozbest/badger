from request_handler.models import Request, User
from django.shortcuts import get_object_or_404

'''Calculates the cost for an invoice to be sent to a student

Assumes a 15 week term.
If students have selected to have recurring sessions, the admins must generate a new invoice before the start
of each term. calculate_cost only generates the cost for a single term.
'''
def calculate_cost(tutor: User, request_id: int)-> float:
    lesson_request = get_object_or_404(Request, id=request_id)
    duration = lesson_request.duration
    frequency = lesson_request.frequency
    lesson_num=calculate_num_lessons(frequency)
    cost = float(tutor.hourly_rate) * float(duration[:-1])  * lesson_num 
    return cost

def calculate_num_lessons(frequency: str) -> int:
    match frequency:
        case "Weekly":
            return 15
        case "Biweekly":
            return 30
        case "Fortnightly":
            return 7