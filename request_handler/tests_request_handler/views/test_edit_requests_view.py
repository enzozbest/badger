from django.test import TestCase
from django.urls import reverse
from tutorials.models import User
from request_handler.models import Request, Modality, Day

INVALID_REQUEST_ID = 999