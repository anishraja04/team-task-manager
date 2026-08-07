from django.urls import path

from . import views

urlpatterns = [
    path("", views.TaskListCreateView.as_view(), name="task-list"),
    path("dashboard/", views.DashboardView.as_view(), name="task-dashboard"),
    path("<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"),
    path("<int:pk>/comments/", views.TaskCommentView.as_view(), name="task-comments"),
]
