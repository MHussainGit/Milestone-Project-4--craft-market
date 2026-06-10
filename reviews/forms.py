from django import forms

from craftmarket.forms import StyledFormMixin

from .models import Review


class ReviewForm(StyledFormMixin, forms.ModelForm):

    class Meta:
        model = Review
        fields = ["rating", "headline", "body"]
        widgets = {
            "rating": forms.RadioSelect,
            "body": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_body(self):
        body = self.cleaned_data.get("body", "").strip()
        if len(body) < 20:
            raise forms.ValidationError(
                "Please write at least 20 characters to help other readers."
            )
        return body
