"""
Accounts views — registration, login, logout, profile, profile deletion.

Pattern mirrors the FitTrack fitness-tracker reference implementation:
- register_view and login_view redirect authenticated users to home.
- All auth-protected views use @login_required.
- profile_delete_view requires a POST request for safety.
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm


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
