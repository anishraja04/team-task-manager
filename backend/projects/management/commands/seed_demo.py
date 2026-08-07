import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Membership, Project
from tasks.models import Task

User = get_user_model()


class Command(BaseCommand):
    help = "This will fill the database with some demo users, projects and tasks so the app does not look empty."

    def handle(self, *args, **options):
        # remove the old english demo users (from earlier version) so nothing looks fake
        User.objects.filter(
            email__in=["alice@example.com", "bob@example.com", "carol@example.com"]
        ).delete()
        Project.objects.filter(
            name__in=["Website Redesign", "Mobile App v2", "Data Migration"]
        ).delete()

        # ---------- create the users first ----------
        admin_user, _ = User.objects.get_or_create(
            email="admin@example.com",
            defaults={"username": "admin", "name": "Admin Sir", "role": User.Role.ADMIN},
        )
        admin_user.set_password("admin12345")
        admin_user.role = User.Role.ADMIN
        admin_user.save()

        # rohan is a final year student who made this project
        rohan, _ = User.objects.get_or_create(
            email="rohan@example.com",
            defaults={"username": "rohan", "name": "Rohan Sharma", "role": User.Role.MEMBER},
        )
        rohan.set_password("password123")
        rohan.save()

        priya, _ = User.objects.get_or_create(
            email="priya@example.com",
            defaults={"username": "priya", "name": "Priya Patel", "role": User.Role.MEMBER},
        )
        priya.set_password("password123")
        priya.save()

        arjun, _ = User.objects.get_or_create(
            email="arjun@example.com",
            defaults={"username": "arjun", "name": "Arjun Verma", "role": User.Role.MEMBER},
        )
        arjun.set_password("password123")
        arjun.save()

        ananya, _ = User.objects.get_or_create(
            email="ananya@example.com",
            defaults={"username": "ananya", "name": "Ananya Iyer", "role": User.Role.MEMBER},
        )
        ananya.set_password("password123")
        ananya.save()

        # ---------- now the projects (college / lab type projects) ----------
        project_data = [
            {
                "name": "Hindi LLM Model Training",
                "description": "Final year project - training a small language model on Hindi wikipedia data.",
                "owner": rohan,
                "members": [priya, arjun],
                "tasks": [
                    ("Collect Hindi wikipedia data", "high", priya),
                    ("Clean the dataset (remove null rows)", "high", None),
                    ("Train tokenizer on hindi corpus", "medium", arjun),
                    ("Run fine-tuning on GPU", "urgent", rohan),
                    ("Evaluate model with perplexity", "medium", priya),
                ],
            },
            {
                "name": "UPI Fraud Detection ML Model",
                "description": "Mini project to detect fraudulent UPI transactions using logistic regression.",
                "owner": priya,
                "members": [ananya],
                "tasks": [
                    ("Download bank transaction dataset", "medium", ananya),
                    ("Handle missing values in data", "high", priya),
                    ("Train the model on 80% data", "high", None),
                    ("Test accuracy on remaining 20%", "medium", ananya),
                ],
            },
            {
                "name": "College Website Backend",
                "description": "Django backend for our college department website (placements info).",
                "owner": arjun,
                "members": [rohan, ananya],
                "tasks": [
                    ("Create student model", "high", rohan),
                    ("Add API for notice board", "medium", ananya),
                    ("Fix the login bug", "urgent", None),
                    ("Deploy on college server", "low", arjun),
                ],
            },
        ]

        # some random status so the dashboard looks real
        all_status = [
            Task.Status.TODO,
            Task.Status.IN_PROGRESS,
            Task.Status.REVIEW,
            Task.Status.DONE,
        ]

        for one_project in project_data:
            project, created = Project.objects.get_or_create(
                name=one_project["name"],
                defaults={
                    "description": one_project["description"],
                    "owner": one_project["owner"],
                },
            )

            # the owner is automatically admin
            Membership.objects.get_or_create(
                project=project,
                user=project.owner,
                defaults={"role": Membership.Role.ADMIN},
            )

            # add other members
            for member in one_project["members"]:
                Membership.objects.get_or_create(
                    project=project,
                    user=member,
                    defaults={"role": Membership.Role.MEMBER},
                )

            # create the tasks
            for title, priority, assignee in one_project["tasks"]:
                task, task_created = Task.objects.get_or_create(
                    project=project,
                    title=title,
                    defaults={
                        "description": "Small task for this project",
                        "priority": priority,
                        "assignee": assignee,
                        "created_by": project.owner,
                        "status": random.choice(all_status),
                        # some tasks are already overdue to test the overdue feature
                        "due_date": date.today() + timedelta(days=random.randint(-3, 14)),
                    },
                )

        self.stdout.write(self.style.SUCCESS("Demo data added successfully! Login users:"))
        self.stdout.write("  admin@example.com   / admin12345")
        self.stdout.write("  rohan@example.com   / password123")
        self.stdout.write("  priya@example.com   / password123")
        self.stdout.write("  arjun@example.com   / password123")
        self.stdout.write("  ananya@example.com  / password123")
