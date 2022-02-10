from mimetypes import init
from re import template
from django.forms import Form
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms import ModelForm, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.models import Task


class GenericFormMixin:
    field_styles = "appearance-none bg-[#F1F5F9] border-2 border-[#F1F5F9] rounded-lg text-gray-700"

    text_field_style = f"w-full leading-tight py-2 px-4 focus:outline-none focus:bg-white focus:border-purple-500 {field_styles}"
    checkbox_style = f"rounded-sm form-check-input appearance-none h-4 w-4 checked:bg-blue-600 checked:border-blue-600 focus:outline-none transition duration-200 mt-1 align-top bg-no-repeat bg-center bg-contain float-left mr-2 cursor-pointer {field_styles}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = self.field_styles


class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        r = Task.objects.filter(deleted=False, user=self.request.user)
        r = r.order_by("priority")
        return r


class UserAuthenticationViewMixin:
    template_name = "user_auth_form.html"
    auth_action = "Auth"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.auth_action
        context["auth_action"] = self.auth_action
        return context


class AuthFormMixin(GenericFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = self.text_field_style


class LoginForm(AuthFormMixin, AuthenticationForm):
    pass


class UserLoginView(UserAuthenticationViewMixin, LoginView):
    form_class = LoginForm
    auth_action = "Login"


class SignUpForm(AuthFormMixin, UserCreationForm):
    pass


class UserSignupView(UserAuthenticationViewMixin, CreateView):
    form_class = SignUpForm
    auth_action = "Sign Up"
    success_url = "/user/login"


class GenericTaskView(AuthorizedTaskManager, ListView):
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


class TaskForm(GenericFormMixin, ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields[0:3]:
            self.fields[field].widget.attrs["class"] = self.text_field_style
        self.fields["completed"].widget.attrs["class"] = self.checkbox_style

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 4:
            raise ValidationError("Too short title")
        return title

    class Meta:
        model = Task
        fields = ["title", "description", "priority", "completed"]


class TaskFormViewMixin(AuthorizedTaskManager):

    form_class = TaskForm
    template_name = "task_form.html"
    success_url = "/tasks"
    task_form_operation = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_header"] = f"{self.task_form_operation} Todo"
        context["task_form_operation"] = self.task_form_operation
        return context

    def ensure_unique_priority(self, priority: int):

        query_result = self.get_queryset().filter(priority=priority)

        if len(query_result) > 1:
            next_task = query_result[0]
            next_task.priority = priority + 1
            next_task.save()
            self.ensure_unique_priority(next_task.priority)


class TaskCreateView(TaskFormViewMixin, CreateView):
    task_form_operation = "Create"

    def form_valid(self, form) -> HttpResponse:
        self.object: Task = form.save()
        self.object.user = self.request.user
        self.object.save()
        self.ensure_unique_priority(self.object.priority)
        return HttpResponseRedirect(self.get_success_url())


class TaskUpdateView(TaskFormViewMixin, UpdateView):
    task_form_operation = "Update"

    def form_valid(self, form) -> HttpResponse:
        super().form_valid(form)
        self.ensure_unique_priority(self.object.priority)
        return HttpResponseRedirect(self.get_success_url())


class GenericTaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_header"] = "Delete Task?"
        return context
