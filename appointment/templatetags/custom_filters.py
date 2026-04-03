from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    try:
        return dictionary.get(int(key))
    except (ValueError, AttributeError):
        return None

@register.filter
def split(value, arg):
    """Split a string by the given separator."""
    return value.split(arg)
