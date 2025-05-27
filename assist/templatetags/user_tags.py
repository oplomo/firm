from django import template
from ..models import Consultant

register = template.Library()


@register.filter
def is_consultant(user):
    return hasattr(user, "consultant_profile")
