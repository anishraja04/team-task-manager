from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProjectListCreateView.as_view(), name="project-list"),
    path("<int:pk>/", views.ProjectDetailView.as_view(), name="project-detail"),
    path("<int:pk>/members/", views.ProjectMembersView.as_view(), name="project-members"),
    path("<int:pk>/members/<int:mpk>/", views.ProjectMemberDetailView.as_view(), name="project-member-detail"),
]
