from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms import ModelForm, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.models import Task


class GenericFormMixin:
    field_styles = "appearance-none bg-[#F1F5F9] border-2 border-[#F1F5F9] rounded-lg text-gray-700"

    text_field_style = (
        f"w-full leading-tight py-2 px-4 focus:outline-none focus:bg-white focus:border-purple-500 {field_styles}"
    )
    checkbox_style = f"rounded-sm form-check-input appearance-none h-4 w-4 checked:bg-blue-600 checked:border-blue-600 focus:outline-none transition duration-200 mt-1 align-top bg-no-repeat bg-center bg-contain float-left mr-2 cursor-pointer {field_styles}"
    choicebox_style = "appearance-none block w-full px-4 py-2 text-xl font-normal text-gray-700 bg-white bg-clip-padding bg-no-repeat border border-solid border-gray-300 rounded transition ease-in-out m-0 focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = self.field_styles


class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)


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
        self.fields["status"].widget.attrs["class"] = self.choicebox_style

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 4:
            raise ValidationError("Too short title")
        return title

    class Meta:
        model = Task
        fields = ["title", "description", "priority", "completed", "status"]


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

    def cascade_update_priorities(self, priority, task_id) -> int:
        deltas = []
        for task in self.get_queryset().filter(completed=False, priority__gte=priority).exclude(id=task_id):
            if task.priority != priority:
                break
            task.priority = priority = priority + 1
            deltas.append(task)
        return Task.objects.bulk_update(deltas, ["priority"])


class TaskCreateView(TaskFormViewMixin, CreateView):
    task_form_operation = "Create"

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        self.object.user = self.request.user
        self.object.save()
        if not self.object.completed:
            self.cascade_update_priorities(self.object.priority, self.object.id)
        return response


class TaskUpdateView(TaskFormViewMixin, UpdateView):
    task_form_operation = "Update"

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        if not form.has_changed():
            return response
        if not self.object.completed and ("priority" in form.changed_data):
            self.cascade_update_priorities(self.object.priority, self.object.id)
        return response


class GenericTaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_header"] = "Delete Task?"
        return context
