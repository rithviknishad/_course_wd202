# Add all your views here

from django.http import HttpResponseRedirect
from django.shortcuts import render

tasks = []
completed_tasks = []


__HTTP_RESPONSE_REDIRECT_TO_TASKS = HttpResponseRedirect("/tasks")


def tasks_view(request):
    return render(
        request,
        "tasks.html",
        {
            "tasks": tasks,
        },
    )


def completed_tasks_view(request):
    return render(
        request,
        "completed_tasks.html",
        {
            "tasks": completed_tasks,
        },
    )


def all_tasks_view(request):
    return render(
        request,
        "all_tasks.html",
        {
            "tasks": [
                *tasks,
                *completed_tasks,
            ],
        },
    )


def add_task_view(request):
    tasks.append(request.GET.get("task"))
    return __HTTP_RESPONSE_REDIRECT_TO_TASKS


def complete_task_view(request, index):
    completed_tasks.append(tasks.pop(index - 1))
    return __HTTP_RESPONSE_REDIRECT_TO_TASKS


def delete_task_view(request, index):
    del tasks[index - 1]
    return __HTTP_RESPONSE_REDIRECT_TO_TASKS
