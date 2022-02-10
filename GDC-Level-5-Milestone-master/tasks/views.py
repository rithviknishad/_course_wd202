# Add your Views Here

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render

from tasks.models import Task


__HTTP_RESPONSE_REDIRECT_TO_TASKS = HttpResponseRedirect("/tasks")


def tasks_view(request: HttpRequest):
    search_term = request.GET.get("search")
    tasks = Task.objects.filter(deleted=False).filter(completed=False)
    if search_term:
        tasks = tasks.filter(title__icontains=search_term)
    ctx = {
        "tasks": tasks,
        "has_pending": bool(tasks),
    }
    return render(request, "tasks.html", ctx)


def completed_tasks_view(request: HttpRequest):
    tasks = Task.objects.filter(deleted=False).filter(completed=True)
    ctx = {
        "tasks": tasks,
    }
    return render(request, "completed_tasks.html", ctx)


def all_tasks_view(request: HttpRequest):
    tasks = Task.objects.filter(deleted=False)
    ctx = {
        "tasks": tasks,
    }
    return render(request, "all_tasks.html", ctx)


def add_task_view(request: HttpRequest):
    Task(title=request.GET.get("task")).save()
    return __HTTP_RESPONSE_REDIRECT_TO_TASKS


def complete_task_view(request: HttpRequest, id):
    Task.objects.filter(id=id).update(completed=True)
    return __HTTP_RESPONSE_REDIRECT_TO_TASKS


def delete_task_view(request: HttpRequest, id):
    Task.objects.filter(id=id).update(deleted=True)
    return __HTTP_RESPONSE_REDIRECT_TO_TASKS
