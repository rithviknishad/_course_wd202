"""task_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from operator import ipow
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.db import router
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from tasks.apiviews import TaskViewSet

router = SimpleRouter()

router.register("api/task", TaskViewSet)

from tasks.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    # For hot-reloading.
    path("__reload__/", include("django_browser_reload.urls")),
    # User Authentication related URLs
    path("user/login/", UserLoginView.as_view()),
    path("user/signup/", UserSignupView.as_view()),
    path("user/logout/", LogoutView.as_view()),
    # Authenticated User's Task Management related URLs
    path("tasks/", AllTaskView.as_view()),
    path("tasks/pending/", PendingTaskView.as_view()),
    path("tasks/completed/", CompletedTaskView.as_view()),
    path("create-task/", TaskCreateView.as_view()),
    path("update-task/<pk>/", TaskUpdateView.as_view()),
    path("delete-task/<pk>/", GenericTaskDeleteView.as_view()),
] + router.urls
