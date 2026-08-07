from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Task(models.Model):
    # status of the task - from todo to done
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW = "review", "In Review"
        DONE = "done", "Done"

    # priority of the task
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # every task belongs to one project
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="tasks")
    # the person who will do this task (can be empty)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    # the person who created this task
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # new tasks should come first in the list
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        # a task is overdue if the due date has passed and it is not done yet
        if self.due_date is None or self.status == self.Status.DONE:
            return False
        return self.due_date < timezone.localdate()

    def clean(self):
        # while creating, due date should not be in the past
        if self.due_date and self.due_date < timezone.localdate() and not self.pk:
            raise ValidationError({"due_date": "Due date cannot be in the past."})

    def save(self, *args, **kwargs):
        # when a task becomes done, we store the completed time automatically
        if self.status == self.Status.DONE and not self.completed_at:
            self.completed_at = timezone.now()
        if self.status != self.Status.DONE:
            self.completed_at = None
        super().save(*args, **kwargs)


class Comment(models.Model):
    # comments are attached to a single task
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_comments")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.email}: {self.body[:30]}"
