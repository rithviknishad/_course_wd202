from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks import models, mixins, forms


class UserLoginView(mixins.AuthViewMixin, LoginView):
    form_class = forms.LoginForm
    auth_action = "Login"


class UserSignupView(mixins.AuthViewMixin, CreateView):
    form_class = forms.SignUpForm
    auth_action = "Sign Up"
    success_url = "/user/login"


class GenericTaskView(mixins.AuthorizedTaskManagerMixin, ListView):
    model = models.Task
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


class TaskCreateView(mixins.TaskFormViewMixin, CreateView):
    task_form_operation = "Create"

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        self.object.user = self.request.user
        self.object.save()
        if not self.object.completed:
            self.cascade_update_priorities(self.object.priority, self.object.id)
        return response


class TaskUpdateView(mixins.TaskFormViewMixin, UpdateView):
    task_form_operation = "Update"

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        if not form.has_changed():
            return response
        if not self.object.completed and ("priority" in form.changed_data):
            self.cascade_update_priorities(self.object.priority, self.object.id)
        return response


class GenericTaskDeleteView(mixins.AuthorizedTaskManagerMixin, DeleteView):
    model = models.Task
    template_name = "task_delete.html"
    success_url = "/tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_header"] = "Delete Task?"
        return context
