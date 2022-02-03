from django import views
from django.contrib import admin
from django.urls import path

from tasks.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tasks/", tasks_view),
    path("completed_tasks/", completed_tasks_view),
    path("all_tasks/", all_tasks_view),
    path("add-task/", add_task_view),
    path("complete_task/<int:id>/", complete_task_view),
    path("delete-task/<int:id>/", delete_task_view),
]
