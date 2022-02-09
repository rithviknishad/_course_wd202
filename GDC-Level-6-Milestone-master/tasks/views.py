from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms import ModelForm, ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.models import Task


class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(
            deleted=False,
            user=self.request.user,
        )


class UserLoginView(LoginView):
    template_name = "user_login.html"


class UserLoginView(LoginView):
    template_name = "user_login.html"


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "user_create.html"  # TODO: implement this template.
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


class TaskCreateForm(ModelForm):
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
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form) -> HttpResponse:
        self.object: Task = form.save()
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class TaskUpdateView(AuthorizedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"


class GenericTaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"
