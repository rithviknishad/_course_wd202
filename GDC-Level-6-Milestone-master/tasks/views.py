from re import template
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms import ModelForm, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.models import Task


class FormStyleMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        style = "bg-[#F1F5F9] appearance-none border-2 border-[#F1F5F9] rounded-lg w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-purple-500"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = style


class __AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)


class __UserAuthenticationViewMixin:
    template_name = "user_auth_form.html"
    auth_action = "Auth"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.auth_action
        context["auth_action"] = self.auth_action
        return context


class LoginForm(FormStyleMixin, AuthenticationForm):
    pass


class UserLoginView(__UserAuthenticationViewMixin, LoginView):
    form_class = LoginForm
    auth_action = "Login"


class SignUpForm(FormStyleMixin, UserCreationForm):
    pass


class UserSignupView(__UserAuthenticationViewMixin, CreateView):
    form_class = SignUpForm
    auth_action = "Sign Up"
    success_url = "/user/login"


class GenericTaskView(__AuthorizedTaskManager, ListView):
    model = Task
    template_name = "tasks.html"
    context_object_name = "tasks"

    def get_tasks_status_description(self):
        all = super().get_queryset()
        completed = all.filter(completed=True)
        return f"{len(completed)} of {len(all)} completed"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_header"] = f"Hi {self.request.user}"
        context["tasks_status_description"] = self.get_tasks_status_description()
        context["page_tabs"] = {
            tab.view_name: (tab.path if self.view_name != tab.view_name else None)
            for tab in [AllTaskView, PendingTaskView, CompletedTaskView]
        }
        return context


class AllTaskView(GenericTaskView):
    view_name = "All"
    path = "/tasks"


class PendingTaskView(GenericTaskView):
    view_name = "Pending"
    path = "/tasks/pending"

    def get_queryset(self):
        return super().get_queryset().filter(completed=False)


class CompletedTaskView(GenericTaskView):
    view_name = "Completed"
    path = "/tasks/completed"

    def get_queryset(self):
        return super().get_queryset().filter(completed=True)


class TaskForm(ModelForm):
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 4:
            raise ValidationError("Too short title")
        return title

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "priority",
            "completed",
        ]


# TODO: test access of this view without authenticating.
class TaskCreateView(__AuthorizedTaskManager, CreateView):
    form_class = TaskForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form) -> HttpResponse:
        self.object: Task = form.save()
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class TaskUpdateView(__AuthorizedTaskManager, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "task_update.html"
    success_url = "/tasks"


class GenericTaskDeleteView(__AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"
