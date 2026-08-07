from django.db.models import Q
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from projects.models import Project
from projects.permissions import IsProjectMember

from .models import Comment, Task
from .serializers import CommentSerializer, TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get("project")
        base = (
            Task.objects.filter(project__owner=user)
            | Task.objects.filter(project__memberships__user=user)
        ).distinct()
        if project_id:
            base = base.filter(project_id=project_id)
        return base

    def get_serializer_context(self):
        context = super().get_serializer_context()
        project_id = self.request.data.get("project") or self.request.query_params.get("project")
        if project_id:
            context["project"] = Project.objects.filter(pk=project_id).first()
        return context

    def perform_create(self, serializer):
        project = serializer.validated_data.get("project")
        if project and not project.is_admin(self.request.user):
            raise PermissionDenied("Only project admins can create tasks.")
        serializer.save()


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsProjectMember]

    def get_queryset(self):
        user = self.request.user
        return (
            Task.objects.filter(project__owner=user)
            | Task.objects.filter(project__memberships__user=user)
        ).distinct()

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if not obj.project.is_member(request.user):
            raise PermissionDenied("You are not a member of this project.")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        is_admin = instance.project.is_admin(request.user)
        is_assignee = instance.assignee_id == request.user.id

        allowed_fields = set(request.data.keys())
        if not is_admin and not is_assignee:
            raise PermissionDenied("Only project admins or the assignee can update this task.")

        if not is_admin:
            # Assignees may only change status/priority of their own task.
            editable = {"status", "priority"}
            forbidden = allowed_fields - editable
            if forbidden:
                raise PermissionDenied(
                    f"Assignees may only update status and priority. Fields blocked: {', '.join(sorted(forbidden))}"
                )
            if "assignee" in allowed_fields and request.data.get("assignee") != instance.assignee_id:
                raise PermissionDenied("Assignees cannot change the assignee.")

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class TaskCommentView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        task = self.get_task()
        return task.comments.all()

    def get_task(self):
        user = self.request.user
        task = (
            Task.objects.filter(project__owner=user)
            | Task.objects.filter(project__memberships__user=user)
        ).filter(pk=self.kwargs["pk"]).first()
        if task is None:
            raise PermissionDenied("Task not found or you are not a member of its project.")
        return task

    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(task=task, author=self.request.user)


class DashboardView(generics.GenericAPIView):
    serializer_class = TaskSerializer

    def get(self, request):
        user = request.user
        tasks = (
            Task.objects.filter(project__owner=user)
            | Task.objects.filter(project__memberships__user=user)
        ).distinct()
        mine = tasks.filter(assignee=user)

        from datetime import date

        return Response(
            {
                "total_tasks": tasks.count(),
                "todo": tasks.filter(status="todo").count(),
                "in_progress": tasks.filter(status="in_progress").count(),
                "review": tasks.filter(status="review").count(),
                "done": tasks.filter(status="done").count(),
                "overdue": tasks.exclude(status="done").filter(due_date__lt=date.today()).count(),
                "my_tasks": mine.count(),
                "my_overdue": mine.exclude(status="done").filter(due_date__lt=date.today()).count(),
                "project_count": Project.objects.filter(
                    Q(owner=user) | Q(memberships__user=user)
                ).distinct().count(),
            }
        )
