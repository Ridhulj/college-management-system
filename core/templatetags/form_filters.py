from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})

@register.filter(name='get_item')
def get_item(value, arg):
    """Return form field by key if value is a form, otherwise dict key."""
    try:
        return value[arg]  # This works for Django forms and dicts
    except (KeyError, AttributeError, TypeError):
        return ''
