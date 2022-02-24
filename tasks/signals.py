from django.db.models.signals import pre_save
from django.dispatch import receiver

from tasks.models import Task, TaskStatusChangeLog


@receiver(pre_save, sender=Task)
def on_task_update(sender, instance: Task, **kwargs) -> None:
    """
    Invoked whenever a create/update operation happens for Task before being saved to DB.
    """
    if instance.id is None:  # New instance being created.
        return
    previous: Task = Task.objects.get(id=instance.id)
    if previous.status != instance.status:
        TaskStatusChangeLog.objects.create(
            task=instance,
            old_status=previous.status,
            new_status=instance.status,
        )
