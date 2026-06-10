"""
Cart forms.

CartAddForm is a plain Form (not a ModelForm) because the cart is
stored in the session, not the database.
"""

from django import forms


class CartAddForm(forms.Form):
    """Validate the quantity the user wants to add to their cart."""

    quantity = forms.IntegerField(min_value=1, max_value=99, initial=1)
    override = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, max_stock=99, **kwargs):
        super().__init__(*args, **kwargs)
        # Store max_stock so clean_quantity can validate against live stock
        self._max_stock = max_stock

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity > self._max_stock:
            raise forms.ValidationError(
                f"Only {self._max_stock} copies are available."
            )
        return quantity
