"""
Accounts forms — registration and login.
"""

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth import get_user_model

from craftmarket.forms import StyledFormMixin

User = get_user_model()


class RegisterForm(StyledFormMixin, UserCreationForm):
    """Extended registration form that also collects an email address."""

    email = forms.EmailField(required=True, help_text="Required. We'll send your order confirmations here.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(StyledFormMixin, AuthenticationForm):
    """Login form with styled widgets."""
    pass


class StyledPasswordResetForm(StyledFormMixin, PasswordResetForm):
    """Password reset request form with the shared 'form-control' styling."""
    pass


class StyledSetPasswordForm(StyledFormMixin, SetPasswordForm):
    """New-password form (reset confirm step) with 'form-control' styling."""
    pass
