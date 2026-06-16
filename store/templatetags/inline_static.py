"""
Template tag for inlining a small static asset directly into the page.

Inlining the (tiny) site stylesheet removes a render-blocking network
request from the critical path without the flash-of-unstyled-content that
asynchronous stylesheet loading would introduce.  ``styles.css`` remains the
single source of truth — it is read at render time rather than duplicated.
"""

from pathlib import Path

from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def inline_static(path):
    """Return the raw contents of a static file for inlining in a tag.

    Resolves the source file via the staticfiles finders, so it works the
    same in development and after ``collectstatic`` in production.
    """
    absolute_path = finders.find(path)
    if not absolute_path:
        return ""
    return mark_safe(Path(absolute_path).read_text(encoding="utf-8"))
