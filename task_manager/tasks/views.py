from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render

from tasks.models import Task


def tasks_view(request: HttpRequest):
    search_term = request.GET.get("search")
    tasks = Task.objects.filter(deleted=False)

    if search_term:
        tasks = tasks.filter(title__icontains=search_term)

    return render(request, "tasks.html", {"tasks": tasks})


def add_task_view(request: HttpRequest):
    task_value = request.GET.get("task")
    Task(title=task_value).save()
    return HttpResponseRedirect("/tasks")


def delete_task_view(request: HttpRequest, index: int):
    Task.objects.filter(id=index).update(deleted=True)
    return HttpResponseRedirect("/tasks")
