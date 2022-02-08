from django.db import models

from django.contrib.auth.models import User


class Task(models.Model):

    title = models.CharField(max_length=100)
    """The title of the task."""

    description = models.TextField()
    """The description of the task."""

    completed = models.BooleanField(default=False)
    """Whether this task has been completed."""

    created_date = models.DateTimeField(auto_now=True)
    """Timestamp of when this task was created."""

    deleted = models.BooleanField(default=False)
    """Whether the task has been deleted."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    """The user that this task belongs to."""

    priority = models.PositiveIntegerField()
    """
    A postive number that represents the priority of the task.
    Lower the value, higher the priority (i.e., 0 has highest priority).
    """

    def __str__(self):
        return self.title
