"""
Shared form utilities used across all CraftMarket apps.

Import StyledFormMixin into any app's forms.py to automatically apply
the 'form-control' CSS class to all visible form fields.
"""


class StyledFormMixin:
    """Add the 'form-control' CSS class to every visible widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            css = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{css} form-control".strip()
