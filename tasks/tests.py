from http import HTTPStatus
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIClient
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from tasks.views import *
from tasks.models import *


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
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman")
        self.user.save()

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
        req.user = self.user
        res = AllTaskView.as_view()(req)
        self.assertEquals(res.status_code, HTTPStatus.OK)

    def test_pending_tasks_view(self):
        req = self.factory.get("/tasks/pending/")
        req.user = self.user
        res = PendingTaskView.as_view()(req)
        self.assertEquals(res.status_code, HTTPStatus.OK)

    def test_completed_tasks_view(self):
        req = self.factory.get("/tasks/completed/")
        req.user = self.user
        res = CompletedTaskView.as_view()(req)
        self.assertEquals(res.status_code, HTTPStatus.OK)

    def test_create_task_view(self):
        req = self.factory.get("/create-task/")
        req.user = self.user
        res = TaskCreateView.as_view()(req)
        self.assertEquals(res.status_code, HTTPStatus.OK)

    def test_report_create_view(self):
        req = self.factory.get("/user/config/report/")
        req.user = self.user
        res = UserReportConfigurationCreateView.as_view()(req)
        self.assertEquals(res.status_code, HTTPStatus.OK)


class ApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman")
        self.user.save()

    def test_tasks_view(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        res = self.client.get("/api/v1/tasks/")
        self.assertEquals(res.status_code, HTTPStatus.OK)

    def test_add_task(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        obj = Task.objects.create(
            title="task",
            description="this is a task",
            priority=1,
            completed=False,
            status=Task.Statuses.PENDING,
            user=self.user,
        )
        obj.save()
        res = self.client.get(f"/api/v1/tasks/{obj.id}/")
        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_status_changes_view(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        res = self.client.get("/api/v1/task-status-changes/")
        self.assertEquals(res.status_code, HTTPStatus.OK)
