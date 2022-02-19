from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import ModelForm, ValidationError

from tasks import models, mixins


class SignUpForm(mixins.AuthFormMixin, UserCreationForm):
    pass


class LoginForm(mixins.AuthFormMixin, AuthenticationForm):
    pass


class TaskForm(mixins.FormStyleMixin, ModelForm):
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
        model = models.Task
        fields = ["title", "description", "priority", "completed", "status"]
