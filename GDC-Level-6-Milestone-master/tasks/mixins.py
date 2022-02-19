from django.contrib.auth.mixins import LoginRequiredMixin

from tasks.models import Task
from tasks.forms import TaskForm


class FormStyleMixin:
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


class AuthorizedTaskManagerMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)


class AuthViewMixin:
    template_name = "user_auth_form.html"
    auth_action = "Auth"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.auth_action
        context["auth_action"] = self.auth_action
        return context


class AuthFormMixin(FormStyleMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = self.text_field_style


class TaskFormViewMixin(AuthorizedTaskManagerMixin):

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
