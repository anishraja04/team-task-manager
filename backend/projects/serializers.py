from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Membership, Project

User = get_user_model()


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=User.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Membership
        fields = ["id", "user", "user_id", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]

    def validate(self, attrs):
        user = attrs.get("user")
        if user is None:
            raise serializers.ValidationError({"user_id": "A user is required."})
        project = self.context["project"]
        if project.memberships.filter(user=user).exists() or project.owner_id == user.id:
            raise serializers.ValidationError({"user_id": "This user is already a member of the project."})
        return attrs

    def create(self, validated_data):
        return Membership.objects.create(project=self.context["project"], **validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = MembershipSerializer(many=True, read_only=True, source="memberships")
    task_count = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    overdue_tasks = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "members",
            "task_count",
            "completed_tasks",
            "overdue_tasks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_completed_tasks(self, obj):
        return obj.tasks.filter(status="done").count()

    def get_overdue_tasks(self, obj):
        from datetime import date

        return obj.tasks.exclude(status="done").filter(due_date__lt=date.today()).count()

    def create(self, validated_data):
        project = Project.objects.create(owner=self.context["request"].user, **validated_data)
        Membership.objects.create(project=project, user=project.owner, role=Membership.Role.ADMIN)
        return project
