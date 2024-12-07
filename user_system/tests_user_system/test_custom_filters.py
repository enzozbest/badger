from django.test import TestCase

from user_system.templatetags.custom_filters import widget_type


class WidgetTypeFilterTest(TestCase):

    def test_handles_non_form_field(self):
        non_field = "Not a form field"
        result = widget_type(non_field)
        self.assertIsNone(result)
