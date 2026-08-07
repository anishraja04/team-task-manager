from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Membership, Project
from .permissions import IsProjectAdmin, IsProjectMember
from .serializers import MembershipSerializer, ProjectSerializer

User = get_user_model()


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_platform_admin:
            return Project.objects.all()
        return Project.objects.filter(
            Q(owner=user) | Q(memberships__user=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save()


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_platform_admin:
            return Project.objects.all()
        return Project.objects.filter(
            Q(owner=user) | Q(memberships__user=user)
        ).distinct()

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ("PUT", "PATCH", "DELETE") and not obj.is_admin(request.user):
            raise PermissionDenied("Only project admins can modify or delete this project.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMembersView(generics.ListCreateAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsProjectAdmin]

    def get_queryset(self):
        project = self.get_project()
        return project.memberships.all()

    def get_project(self):
        user = self.request.user
        return generics.get_object_or_404(
            Project.objects.filter(
                Q(owner=user) | Q(memberships__user=user)
            ).distinct(),
            pk=self.kwargs["pk"],
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["project"] = self.get_project()
        return context

    def create(self, request, *args, **kwargs):
        project = self.get_project()
        if not project.is_admin(request.user):
            raise PermissionDenied("Only project admins can manage team members.")
        return super().create(request, *args, **kwargs)


class ProjectMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsProjectAdmin]
    lookup_url_kwarg = "mpk"

    def get_queryset(self):
        return Membership.objects.filter(project_id=self.kwargs["pk"])

    def destroy(self, request, *args, **kwargs):
        membership = self.get_object()
        project = membership.project
        if project.owner_id == membership.user_id:
            return Response(
                {"detail": "The project owner cannot be removed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(membership)
        return Response(status=status.HTTP_204_NO_CONTENT)
