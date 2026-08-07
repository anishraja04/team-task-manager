from django.conf import settings
from django.db import models


class Membership(models.Model):
    """
    Tells us which role a user has inside a project.
    A user can be admin or member in one project and
    something else in another project, that is why this is a separate model.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # one user can be added only once in one project
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user.email} -> {self.project.name} ({self.role})"


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # the person who created the project becomes the owner
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
        # platform admin is always treated as admin
        membership = self.memberships.filter(user=user).first()
        return (
            membership.role == Membership.Role.ADMIN
            if membership
            else (self.owner_id == user.id or user.is_platform_admin)
        )

    def is_member(self, user):
        return self.memberships.filter(user=user).exists() or self.owner_id == user.id or user.is_platform_admin
