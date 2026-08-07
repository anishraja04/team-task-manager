from django.conf import settings
from django.db import models


class Membership(models.Model):
    """Role of a user inside a project (Admin/Member)."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user.email} -> {self.project.name} ({self.role})"


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Membership",
        related_name="projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_admin(self, user):
        membership = self.memberships.filter(user=user).first()
        return (
            membership.role == Membership.Role.ADMIN
            if membership
            else (self.owner_id == user.id or user.is_platform_admin)
        )

    def is_member(self, user):
        return self.memberships.filter(user=user).exists() or self.owner_id == user.id or user.is_platform_admin
