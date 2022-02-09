from re import template
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms import ModelForm, ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.models import Task


class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)


class UserAuthFormViewMixin:
    template_name = "user_auth_form.html"
    auth_action = "Auth"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.auth_action
        context["auth_action"] = self.auth_action
        return context


class FormStyleMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes trailing colon present in form field labels.
        # Apply style to all form fields.
        style = "bg-[#F1F5F9] appearance-none border-2 border-[#F1F5F9] rounded-lg w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-purple-500"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = style


class LoginForm(FormStyleMixin, AuthenticationForm):
    pass


class SignUpForm(FormStyleMixin, UserCreationForm):
    pass


class UserLoginView(UserAuthFormViewMixin, LoginView):
    form_class = LoginForm
    auth_action = "Login"


class UserCreateView(UserAuthFormViewMixin, CreateView):
    form_class = SignUpForm
    auth_action = "Sign Up"
    success_url = "/user/login"


class GenericTaskView(AuthorizedTaskManager, ListView):
    template_name = "tasks.html"


class AllTaskView(GenericTaskView):
    pass


class PendingTaskView(GenericTaskView):
    def get_queryset(self):
        return super().get_queryset().filter(completed=False)


class CompletedTaskView(GenericTaskView):
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
class TaskCreateView(AuthorizedTaskManager, CreateView):
    form_class = TaskForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form) -> HttpResponse:
        self.object: Task = form.save()
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class TaskUpdateView(AuthorizedTaskManager, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "task_update.html"
    success_url = "/tasks"


class GenericTaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"
