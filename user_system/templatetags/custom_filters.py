from django import template

register = template.Library()

@register.filter
def widget_type(field):
    """Returns the widget type for a form field."""
    try:
        return field.field.widget.__class__.__name__
    except AttributeError:
        return None
