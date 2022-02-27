from celery.task import periodic_task
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
import inspect

from tasks.models import Task, UserReportConfiguration
from datetime import datetime

__report_email_subject = subject = "Daily Report | Todo Manager"


def __report_email_body(user: User) -> str:
    # TODO: show only last 1 days changes by reading task status history instead of cummulative results.
    tasks = Task.objects.filter(deleted=False, user=user)
    pending = tasks.filter(status=Task.Statuses.PENDING).count()
    in_progress = tasks.filter(status=Task.Statuses.IN_PROGRESS).count()
    completed = tasks.filter(status=Task.Statuses.COMPLETED).count()
    cancelled = tasks.filter(status=Task.Statuses.CANCELLED).count()
    # TODO: make the numbers bold
    return inspect.cleandoc(
        f"""
        Hey {user.get_full_name() or user.username},

        Here's your daily tasks report.

        You've completed {completed} tasks so far! Great!
        You have {in_progress} tasks in progress and {pending} tasks pending.
        Looks like you've cancelled {cancelled} tasks so far.

        ---

        From your favourite Todo Manager!!
        Have a great day :)
    """
    )


@periodic_task(run_every=timedelta(seconds=10))
def dispatch_user_reports():
    now = datetime.now()
    for report_config in UserReportConfiguration.objects.filter(
        enabled=True,
        last_dispatched__lt=(now - timedelta(days=1)),
    ):
        report_config: UserReportConfiguration = report_config
        user: User = User.objects.get(id=report_config.user.id)
        send_mail(
            subject=__report_email_subject,
            message=__report_email_body(user),
            from_email="bot@tasks_manager.io",
            recipient_list=[user.email],
        )
        dt = report_config.dispatch_time
        report_config.last_dispatched = now.replace(hour=dt.hour, minute=dt.minute)
        report_config.save(update_fields=["last_dispatched"])
