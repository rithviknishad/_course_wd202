import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.forms import LoginForm, SignUpForm, TaskForm, UserReportConfigurationForm
from tasks.mixins import AuthorizedTaskManagerMixin, AuthViewMixin
from tasks.models import Task, UserReportConfiguration


class UserLoginView(AuthViewMixin, LoginView):
    form_class = LoginForm
    auth_action = "Login"


class UserSignupView(AuthViewMixin, CreateView):
    form_class = SignUpForm
    auth_action = "Sign Up"
    success_url = "/user/login"


class GenericTaskView(AuthorizedTaskManagerMixin, ListView):
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
        user_report_config = UserReportConfiguration.objects.filter(user=self.request.user)
        context["user_report_config_url"] = (
            f"/user/config/report/{user_report_config[0].id}/" if user_report_config else "/user/config/report/"
        )
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


class GenericTaskFormView(AuthorizedTaskManagerMixin):

    form_class = TaskForm
    template_name = "task_form.html"
    success_url = "/tasks"
    task_form_operation = None

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


class TaskCreateView(GenericTaskFormView, CreateView):
    task_form_operation = "Create"

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        self.object.user = self.request.user
        self.object.save()
        if not self.object.completed:
            self.cascade_update_priorities(self.object.priority, self.object.id)
        return response


class TaskUpdateView(GenericTaskFormView, UpdateView):
    task_form_operation = "Update"

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        if not form.has_changed():
            return response
        if not self.object.completed and ("priority" in form.changed_data):
            self.cascade_update_priorities(self.object.priority, self.object.id)
        return response


class GenericTaskDeleteView(AuthorizedTaskManagerMixin, DeleteView):
    template_name = "task_delete.html"
    success_url = "/tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_header"] = "Delete Task?"
        return context


class UserReportConfigurationCreateView(LoginRequiredMixin, CreateView):
    form_class = UserReportConfigurationForm
    template_name = "user_report_config.html"
    success_url = "/tasks"

    def get(self, request, *args, **kwargs) -> HttpResponse:

        # redirects to existing user report config, if already exists.
        config_report = UserReportConfiguration.objects.filter(user=self.request.user.id)
        if config_report:
            return HttpResponseRedirect(f"/user/config/report/{config_report[0].id}")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        self.object.user = self.request.user
        self.object.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_header"] = f"Report Configurations"
        return context


class UserReportConfigurationUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserReportConfigurationForm
    template_name = "user_report_config.html"
    success_url = "/tasks"

    def get_queryset(self):
        qs = UserReportConfiguration.objects.filter(user=self.request.user.id)
        if qs is None:
            UserReportConfiguration.objects.create(
                user=self.request.user,
                dispatch_time=datetime.time(10, 0, 0),
            ).save()
            qs = UserReportConfiguration.objects.filter(user=self.request.user.id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_header"] = f"Report Configurations"
        return context
