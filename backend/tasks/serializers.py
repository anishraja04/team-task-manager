from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Comment, Task

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "task", "author", "body", "created_at"]
        read_only_fields = ["id", "task", "author", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    # these extra fields are for showing full details on the frontend
    assignee_detail = UserSerializer(source="assignee", read_only=True)
    created_by = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "project",
            "project_name",
            "assignee",
            "assignee_detail",
            "created_by",
            "status",
            "priority",
            "due_date",
            "is_overdue",
            "completed_at",
            "created_at",
            "updated_at",
            "comments",
        ]
        read_only_fields = ["id", "created_by", "completed_at", "created_at", "updated_at"]

    def validate_assignee(self, value):
        # checking that we only assign the task to someone who is in the project
        project = self.instance.project if self.instance else self.context.get("project")
        if project is None:
            raise serializers.ValidationError("This task must belong to a project.")
        if value is not None and not project.is_member(value):
            raise serializers.ValidationError("Assignee must be a member of this project.")
        return value

    def validate_project(self, value):
        # user should not create task in some project where he is not a member
        user = self.context["request"].user
        if not value.is_member(user):
            raise serializers.ValidationError("You are not a member of this project.")
        return value

    def create(self, validated_data):
        # set the creator as the current logged in user
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
