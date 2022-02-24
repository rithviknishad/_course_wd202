from django.contrib import admin

# Register your models here.

from tasks.models import Task, TaskStatusChangeLog, UserReportConfiguration

admin.sites.site.register(Task)
admin.sites.site.register(TaskStatusChangeLog)
admin.sites.site.register(UserReportConfiguration)
