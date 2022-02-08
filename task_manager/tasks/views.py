import imp
from re import template

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms import ModelForm, ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.models import Task


class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)


class UserLoginView(LoginView):
    template_name = "user_login.html"


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login"


def session_storage_view(request: HttpRequest):
    total_views = request.session.get("total_views", 0)
    request.session["total_views"] = total_views + 1
    return HttpResponse(f"Total Views is {total_views} and the user is {request.user}")


class GenericTaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"


class GenericTaskDetailView(AuthorizedTaskManager, DetailView):
    model = Task
    template_name = "task_detail.html"


class TaskCreateForm(ModelForm):
    def clean_title(self):

        title = self.cleaned_data["title"]
        if len(title) < 10:
            raise ValidationError("Data too small")
        return title.upper()

    class Meta:
        model = Task
        fields = ["title", "description", "completed"]


class GenericTaskCreateView(CreateView):
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form) -> HttpResponse:
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
        # return super().form_valid(form)


class GenericTaskUpdateView(AuthorizedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"


class GenericTaskView(AuthorizedTaskManager, ListView):
    queryset = Task.objects.filter(deleted=False)
    template_name = "tasks.html"
    context_object_name = "tasks"

    paginate_by = 5

    def get_queryset(self):
        tasks = Task.objects.filter(
            deleted=False,
            user=self.request.user,
        )
        search_term = self.request.GET.get("search")
        if search_term:
            tasks = tasks.filter(title__icontains=search_term)
        return tasks


class TaskView(View):
    def get(self, request: HttpRequest):
        search_term = request.GET.get("search")
        tasks = Task.objects.filter(deleted=False)
        if search_term:
            tasks = tasks.filter(title__icontains=search_term)
        return render(request, "tasks.html", {"tasks": tasks})


class CreateTaskView(View):
    def get(self, request: HttpRequest):
        return render(request, "task_create.html")

    def post(self, request: HttpRequest):
        task_value = request.POST.get("task")
        Task(title=task_value).save()
        return HttpResponseRedirect("/tasks")


def tasks_view(request: HttpRequest):
    search_term = request.GET.get("search")
    tasks = Task.objects.filter(deleted=False)

    if search_term:
        tasks = tasks.filter(title__icontains=search_term)

    return render(request, "tasks.html", {"tasks": tasks})


def delete_task_view(request: HttpRequest, index: int):
    Task.objects.filter(id=index).update(deleted=True)
    return HttpResponseRedirect("/tasks")
