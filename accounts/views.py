"""
Accounts views — registration, login, logout, profile, profile deletion.

Pattern mirrors the FitTrack fitness-tracker reference implementation:
- register_view and login_view redirect authenticated users to home.
- All auth-protected views use @login_required.
- profile_delete_view requires a POST request for safety.
"""

import logging

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm

logger = logging.getLogger(__name__)


def register_view(request):
    """Register a new user account. Redirects authenticated users away."""
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome to CraftMarket, {user.username}!")
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Log in an existing user. Redirects authenticated users away."""
    if request.user.is_authenticated:
        return redirect("home")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        next_url = request.GET.get("next") or "home"
        messages.success(request, "Welcome back!")
        return redirect(next_url)
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """Log out the current user (POST only to prevent CSRF issues)."""
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def profile_view(request):
    """Show the authenticated user's profile and order summary."""
    from checkout.models import Order
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "accounts/profile.html", {
        "orders": orders,
    })


@login_required
def profile_delete_view(request):
    """Delete the authenticated user's account (POST only)."""
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("home")
    return render(request, "accounts/profile_delete.html")


class GracefulPasswordResetView(auth_views.PasswordResetView):
    """Password reset that never 500s when the email fails to send.

    The default view sends the reset email synchronously, so any SMTP
    problem (provider outage, rejected recipient, rate limit) raises and
    becomes a Server Error. Here we log the failure and still redirect to
    the 'done' page — which also preserves the standard behaviour of not
    revealing whether an email address has an account.
    """

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception:
            logger.exception(
                "Password reset email failed to send for %r",
                form.cleaned_data.get("email"),
            )
            return redirect(self.get_success_url())
