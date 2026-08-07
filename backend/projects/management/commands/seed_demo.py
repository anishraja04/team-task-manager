import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Membership, Project
from tasks.models import Task

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo users, projects and tasks."

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            email="admin@example.com",
            defaults={"username": "admin", "name": "Platform Admin", "role": User.Role.ADMIN},
        )
        admin.set_password("admin12345")
        admin.role = User.Role.ADMIN
        admin.save()

        alice, _ = User.objects.get_or_create(
            email="alice@example.com",
            defaults={"username": "alice", "name": "Alice Johnson", "role": User.Role.MEMBER},
        )
        alice.set_password("password123")
        alice.save()

        bob, _ = User.objects.get_or_create(
            email="bob@example.com",
            defaults={"username": "bob", "name": "Bob Smith", "role": User.Role.MEMBER},
        )
        bob.set_password("password123")
        bob.save()

        carol, _ = User.objects.get_or_create(
            email="carol@example.com",
            defaults={"username": "carol", "name": "Carol Davis", "role": User.Role.MEMBER},
        )
        carol.set_password("password123")
        carol.save()

        project_data = [
            {
                "name": "Website Redesign",
                "description": "Revamp the marketing website with a modern look.",
                "owner": alice,
                "members": [bob, carol],
                "tasks": [
                    ("Design new landing page", "high", bob),
                    ("Build component library", "medium", carol),
                    ("Migrate content", "low", None),
                    ("QA pass on responsive layout", "urgent", bob),
                ],
            },
            {
                "name": "Mobile App v2",
                "description": "Second major release of the mobile application.",
                "owner": bob,
                "members": [alice],
                "tasks": [
                    ("Implement offline sync", "urgent", alice),
                    ("Update push notifications", "medium", None),
                    ("Performance profiling", "high", bob),
                ],
            },
            {
                "name": "Data Migration",
                "description": "Move legacy customer data to the new warehouse.",
                "owner": carol,
                "members": [alice, bob],
                "tasks": [
                    ("Write ETL scripts", "high", alice),
                    ("Validate transformed records", "medium", bob),
                    ("Schedule nightly job", "low", None),
                ],
            },
        ]

        statuses = [Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW, Task.Status.DONE]
        for proj in project_data:
            project, _ = Project.objects.get_or_create(
                name=proj["name"],
                defaults={"description": proj["description"], "owner": proj["owner"]},
            )
            Membership.objects.get_or_create(
                project=project, user=project.owner, defaults={"role": Membership.Role.ADMIN}
            )
            for member in proj["members"]:
                Membership.objects.get_or_create(
                    project=project,
                    user=member,
                    defaults={"role": Membership.Role.MEMBER},
                )
            for title, priority, assignee in proj["tasks"]:
                task, created = Task.objects.get_or_create(
                    project=project,
                    title=title,
                    defaults={
                        "description": f"Demo task: {title}",
                        "priority": priority,
                        "assignee": assignee,
                        "created_by": project.owner,
                        "status": random.choice(statuses),
                        "due_date": date.today() + timedelta(days=random.randint(-3, 14)),
                    },
                )
                if not created and task.status == Task.Status.DONE:
                    task.save()

        self.stdout.write(self.style.SUCCESS("Seed complete. Login users:"))
        self.stdout.write("  admin@example.com / admin12345  (platform admin)")
        self.stdout.write("  alice@example.com / password123")
        self.stdout.write("  bob@example.com   / password123")
        self.stdout.write("  carol@example.com / password123")
