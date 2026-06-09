from django import forms

from craftmarket.forms import StyledFormMixin

from .models import Category, Product, Shop


class ProductForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title", "category", "description", "materials",
            "made_to_order", "price", "stock", "image_url", "featured",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "image_url": forms.URLInput(attrs={"placeholder": "https://..."}),
            "materials": forms.TextInput(attrs={"placeholder": "e.g. oak, beeswax, linen"}),
        }

    def __init__(self, *args, shop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._shop = shop

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price


class ShopForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Shop
        fields = ["name", "description", "location", "image_url"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "image_url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Shop name cannot be blank.")
        return name


class CategoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Category name cannot be blank.")
        return name
