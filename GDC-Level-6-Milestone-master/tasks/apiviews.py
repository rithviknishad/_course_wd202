from django.contrib.auth.models import User
from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    CharFilter,
    BooleanFilter,
    DateTimeFromToRangeFilter,
    ChoiceFilter,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from tasks.models import Task, TaskStatusChangeLog


class UserSerializer(ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")


class TaskSerializer(ModelSerializer):
    """Serializer for Task model."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "description", "priority", "completed", "user", "status"]


class TaskFilter(FilterSet):
    """Filter sets for Tasks."""

    title = CharFilter(lookup_expr="icontains")
    completed = BooleanFilter()


class TaskViewSet(ModelViewSet):
    """Model View Set for Tasks"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskStatusChangeLogSerializer(ModelSerializer):
    class TaskSerializer(ModelSerializer):
        """Serializer for Task model."""

        class Meta:
            model = Task
            fields = ["id", "title", "description"]

    task = TaskSerializer(read_only=True)

    class Meta:
        model = TaskStatusChangeLog
        fields = ["task", "timestamp", "old_status", "new_status"]


class TaskStatusChangesFilter(FilterSet):
    """Filter sets for Tasks."""

    timestamp = DateTimeFromToRangeFilter(field_name="timestamp", label="Date")
    old_status = ChoiceFilter(choices=Task.StatusChoices.choices)
    new_status = ChoiceFilter(choices=Task.StatusChoices.choices)


class TaskStatusChangesViewSet(ReadOnlyModelViewSet):
    """Model View Set for Task Status Changes Log model."""

    queryset = TaskStatusChangeLog.objects.all()
    serializer_class = TaskStatusChangeLogSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskStatusChangesFilter
