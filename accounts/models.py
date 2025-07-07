from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Account(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("additional_docs_required", "Additional Documents Required"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    phone_number = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Admin fields
    rejection_reason = models.TextField(blank=True, null=True)
    additional_docs_reason = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="reviewed_accounts",
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

    def clean(self):
        if self.status == "rejected" and not self.rejection_reason:
            raise ValidationError(
                {
                    "rejection_reason": "Rejection reason is required when status is rejected"
                }
            )
        if (
            self.status == "additional_docs_required"
            and not self.additional_docs_reason
        ):
            raise ValidationError(
                {
                    "additional_docs_reason": "Additional documents reason is required when status is additional documents required."
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
