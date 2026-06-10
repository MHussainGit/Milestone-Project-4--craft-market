"""
Checkout forms — shipping address collection.

Card details are handled entirely by Stripe Elements (client-side JS)
and never pass through Django's server.
"""

from django import forms

from craftmarket.forms import StyledFormMixin

from .models import Order


class ShippingForm(StyledFormMixin, forms.ModelForm):
    """Collect the delivery address for an order."""

    class Meta:
        model = Order
        fields = [
            "full_name", "email",
            "address_line1", "address_line2",
            "city", "postcode", "country",
        ]
        widgets = {
            "address_line2": forms.TextInput(attrs={"placeholder": "Flat, suite, etc. (optional)"}),
        }

    def clean_postcode(self):
        postcode = self.cleaned_data.get("postcode", "").strip()
        if not postcode:
            raise forms.ValidationError("Postcode is required.")
        return postcode
