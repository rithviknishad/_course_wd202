from django.contrib import admin
from django.urls import path

import tasks.views as views

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("tasks/", views.tasks_view),
    path("completed-tasks/", views.completed_tasks_view),
    path("all-tasks/", views.all_tasks_view),
    path("add-task/", views.add_task_view),
    path("complete-task/<int:index>", views.complete_task_view),
    path("delete-task/<int:index>", views.delete_task_view),
]
