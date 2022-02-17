from django.db import models

from django.contrib.auth.models import User


class Task(models.Model):
    class Meta:
        ordering = ("completed", "priority")

    class StatusChoices(models.TextChoices):
        PENDING = "Pending", "Pending"
        IN_PROGRESS = "In Progress", "In Progress"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"

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

    status = models.CharField(max_length=100, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    """
    The current status of the task.
    """

    def __str__(self):
        return self.title


class TaskStatusChangeLog(models.Model):
    """Model class for task status change event records."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    """The task this status change log is associated to."""

    timestamp = models.DateTimeField(auto_now=True)
    """The timestamp when the status change event occurred."""

    old_status = models.CharField(max_length=100, choices=Task.StatusChoices.choices)
    """The status of the task before updating the new status."""

    new_status = models.CharField(max_length=100, choices=Task.StatusChoices.choices)
    """The new status the task is updated to."""
