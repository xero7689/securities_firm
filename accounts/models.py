import structlog
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

logger = structlog.get_logger(__name__)


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
    reviewed_at = models.DateTimeField(blank=True, null=True)

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

        # Get the original object from database to compare changes
        original_obj = None
        is_new = self.pk is None

        if not is_new:
            try:
                original_obj = Account.objects.get(pk=self.pk)
            except Account.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Log audit record
        if is_new:
            # Log when new account is created
            logger.info(
                "new_account_created",
                user_id=self.user.id,
                username=self.user.username,
                user_email=self.user.email,
                account_id=self.id,
                status=self.status,
                phone_number=self.phone_number,
                address=self.address,
                created_at=self.created_at.isoformat() if self.created_at else None,
                event_type="account_creation",
                change_method="model_save",
            )
        elif original_obj and original_obj.status != self.status:
            # Log when account status changes
            logger.info(
                "account_status_changed",
                user_id=self.user.id,
                username=self.user.username,
                user_email=self.user.email,
                account_id=self.id,
                previous_status=original_obj.status,
                new_status=self.status,
                reviewer_id=self.reviewed_by.id if self.reviewed_by else None,
                reviewer_username=self.reviewed_by.username
                if self.reviewed_by
                else None,
                reviewer_email=self.reviewed_by.email if self.reviewed_by else None,
                reviewed_at=self.reviewed_at.isoformat() if self.reviewed_at else None,
                approved_at=self.approved_at.isoformat() if self.approved_at else None,
                rejection_reason=self.rejection_reason,
                additional_docs_reason=self.additional_docs_reason,
                phone_number=self.phone_number,
                address=self.address,
                event_type="status_change",
                change_method="model_save",
            )
