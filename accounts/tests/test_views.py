"""
Accounts view tests.

Run with: pytest accounts/tests/test_views.py -v
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_returns_200(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_register_redirects_authenticated_user(self):
        User.objects.create_user("existing", password="pass")
        self.client.login(username="existing", password="pass")
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_register_post_creates_user(self):
        count_before = User.objects.count()
        self.client.post(reverse("register"), {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "Str0ngPass!",
            "password2": "Str0ngPass!",
        })
        self.assertEqual(User.objects.count(), count_before + 1)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_post_logs_in_user(self):
        self.client.post(reverse("register"), {
            "username": "newuser2",
            "email": "new2@example.com",
            "password1": "Str0ngPass!",
            "password2": "Str0ngPass!",
        })
        response = self.client.get(reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_register_post_duplicate_email_fails(self):
        User.objects.create_user("existing", email="taken@example.com", password="pass")
        response = self.client.post(reverse("register"), {
            "username": "anotheruser",
            "email": "taken@example.com",
            "password1": "Str0ngPass!",
            "password2": "Str0ngPass!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "email", "An account with this email address already exists.")

    def test_register_post_password_mismatch_fails(self):
        response = self.client.post(reverse("register"), {
            "username": "mismatch",
            "email": "x@example.com",
            "password1": "Str0ngPass!",
            "password2": "DifferentPass!",
        })
        self.assertEqual(response.status_code, 200)


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("loginuser", password="Str0ngPass!")

    def test_login_returns_200(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_redirects_authenticated_user(self):
        self.client.login(username="loginuser", password="Str0ngPass!")
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("home"))

    def test_login_post_logs_in_user(self):
        self.client.post(reverse("login"), {
            "username": "loginuser",
            "password": "Str0ngPass!",
        })
        response = self.client.get(reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_post_bad_credentials_fails(self):
        response = self.client.post(reverse("login"), {
            "username": "loginuser",
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, 200)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("logoutuser", password="pass")

    def test_logout_post_logs_out_user(self):
        self.client.login(username="logoutuser", password="pass")
        self.client.post(reverse("logout"))
        response = self.client.get(reverse("home"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_redirects_to_home(self):
        self.client.login(username="logoutuser", password="pass")
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("profileuser", password="pass")

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_profile_returns_200_for_authenticated(self):
        self.client.login(username="profileuser", password="pass")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_profile_delete_post_removes_user(self):
        self.client.login(username="profileuser", password="pass")
        pk = self.user.pk
        self.client.post(reverse("profile_delete"))
        self.assertFalse(User.objects.filter(pk=pk).exists())

    def test_profile_delete_logs_out(self):
        self.client.login(username="profileuser", password="pass")
        self.client.post(reverse("profile_delete"))
        response = self.client.get(reverse("home"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
