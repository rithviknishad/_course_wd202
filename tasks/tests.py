from http import HTTPStatus
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from .views import *


class UnauthenticatedViewTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_user_login_view(self):
        res = self.client.get("/user/login/")
        self.assertEquals(res.status_code, HTTPStatus.OK)

    def test_user_signup_view(self):
        res = self.client.get("/user/signup/")
        self.assertEquals(res.status_code, HTTPStatus.OK)

    def test_user_logout_view(self):
        res = self.client.get("/user/logout/")
        self.assertEquals(res.status_code, HTTPStatus.FOUND)
        self.assertEquals(res.url, "/user/login/")

    def test_tasks_view(self):
        req = self.factory.get("/tasks/")
        req.user = AnonymousUser()
        res = AllTaskView.as_view()(req)
        self.assertEquals(res.status_code, HTTPStatus.FOUND)
        self.assertEqual(res.url, "/user/login/?next=/tasks/")


class AuthenticatedViewTests(TestCase):
    pass


class UnauthenticatedApiViewTests(TestCase):
    pass


class AuthenticatedApiViewTests(TestCase):
    pass
