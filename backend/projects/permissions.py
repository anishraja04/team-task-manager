from rest_framework import permissions


def _resolve_project(obj):
    """Resolve the related project from any model instance."""
    if obj.__class__.__name__ == "Project":
        return obj
    if obj.__class__.__name__ == "Task":
        return obj.project
    if obj.__class__.__name__ == "Membership":
        return obj.project
    return None


class IsProjectMember(permissions.BasePermission):
    """Allow only project members (or platform admins)."""

    def has_object_permission(self, request, view, obj):
        project = _resolve_project(obj)
        return project is not None and project.is_member(request.user)


class IsProjectAdmin(permissions.BasePermission):
    """Allow only project admins (or platform admins)."""

    def has_object_permission(self, request, view, obj):
        project = _resolve_project(obj)
        return project is not None and project.is_admin(request.user)
