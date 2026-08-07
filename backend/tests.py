from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Membership, Project
from tasks.models import Task

User = get_user_model()


class AuthAPITests(APITestCase):
    def test_register_login_and_me(self):
        resp = self.client.post(
            "/api/auth/register/",
            {"email": "new@example.com", "username": "newuser", "name": "New User", "password": "strongpass123"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", resp.data)
        self.assertEqual(resp.data["user"]["role"], "member")

        resp = self.client.post(
            "/api/auth/login/", {"email": "new@example.com", "password": "strongpass123"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], "new@example.com")

    def test_login_wrong_password(self):
        resp = self.client.post(
            "/api/auth/login/", {"email": "nobody@example.com", "password": "wrong"}
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_email_rejected(self):
        self.client.post(
            "/api/auth/register/",
            {"email": "dup@example.com", "username": "u1", "password": "strongpass123"},
        )
        resp = self.client.post(
            "/api/auth/register/",
            {"email": "dup@example.com", "username": "u2", "password": "strongpass123"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class RBACTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email="admin@x.com", username="adminx", password="pass12345")
        self.member = User.objects.create_user(email="member@x.com", username="memberx", password="pass12345")
        self.other = User.objects.create_user(email="other@x.com", username="otherx", password="pass12345")
        self.project = Project.objects.create(name="Proj", owner=self.admin)
        Membership.objects.create(project=self.project, user=self.admin, role=Membership.Role.ADMIN)
        Membership.objects.create(project=self.project, user=self.member, role=Membership.Role.MEMBER)

        self._auth(self.admin)

    def _auth(self, user):
        resp = self.client.post("/api/auth/login/", {"email": user.email, "password": "pass12345"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_project_owner_can_create_task(self):
        resp = self.client.post(
            "/api/tasks/",
            {"title": "T1", "project": self.project.id, "assignee": self.member.id},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["created_by"]["id"], self.admin.id)

    def test_member_cannot_create_task(self):
        self._auth(self.member)
        resp = self.client.post(
            "/api/tasks/",
            {"title": "T1", "project": self.project.id, "assignee": self.admin.id},
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_assignee_can_update_status_only(self):
        task = Task.objects.create(title="T1", project=self.project, assignee=self.member, created_by=self.admin)
        self._auth(self.member)
        resp = self.client.patch(f"/api/tasks/{task.id}/", {"status": "in_progress"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.patch(f"/api/tasks/{task.id}/", {"title": "Hacked"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_member_cannot_see_task(self):
        task = Task.objects.create(title="T1", project=self.project, assignee=self.member, created_by=self.admin)
        self._auth(self.other)
        resp = self.client.get(f"/api/tasks/{task.id}/")
        # Not found (404) so non-members cannot infer task existence.
        self.assertIn(resp.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_assignee_must_be_project_member(self):
        resp = self.client.post(
            "/api/tasks/",
            {"title": "T1", "project": self.project.id, "assignee": self.other.id},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_can_add_comment(self):
        task = Task.objects.create(title="T1", project=self.project, assignee=self.member, created_by=self.admin)
        self._auth(self.member)
        resp = self.client.post(f"/api/tasks/{task.id}/comments/", {"body": "Looking good"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["author"]["id"], self.member.id)

    def test_project_membership_management(self):
        self._auth(self.admin)
        resp = self.client.post(
            f"/api/projects/{self.project.id}/members/", {"user_id": self.other.id, "role": "member"}
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        self._auth(self.member)
        resp = self.client.post(
            f"/api/projects/{self.project.id}/members/", {"user_id": self.other.id, "role": "member"}
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_cannot_be_removed(self):
        membership = self.project.memberships.get(user=self.admin)
        resp = self.client.delete(f"/api/projects/{self.project.id}/members/{membership.id}/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dashboard_counts(self):
        Task.objects.create(title="T1", project=self.project, assignee=self.member, created_by=self.admin)
        resp = self.client.get("/api/tasks/dashboard/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["total_tasks"], 1)
        self.assertEqual(resp.data["project_count"], 1)
