from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import Account


class AccountAdminForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        _ = cleaned_data.get("status")
        _ = cleaned_data.get("reviewed_by")

        return cleaned_data


@admin.register(Account)
class ApplicationAdmin(admin.ModelAdmin):
    form = AccountAdminForm
    list_display = [
        "user",
        "status",
        "reviewed_by",
        "reviewed_at",
        "created_at",
        "updated_at",
    ]
    list_filter = ["status", "reviewed_by", "created_at", "updated_at"]
    search_fields = ["user__username", "user__email", "phone_number"]
    readonly_fields = ["created_at", "updated_at", "user", "reviewed_by", "reviewed_at"]
    list_per_page = 25

    fieldsets = (
        (
            "Application Information",
            {"fields": ("user", "phone_number", "address")},
        ),
        (
            "Status Management",
            {"fields": ("status", "rejection_reason", "additional_docs_reason")},
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "approved_at",
                    "reviewed_by",
                    "reviewed_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        try:
            # Set reviewed_by and reviewed_at for any non-pending status if not already set
            if obj.status != "pending" and not obj.reviewed_by:
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()

            # Set approved_at when status changes to approved
            if obj.status == "approved" and not obj.approved_at:
                obj.approved_at = timezone.now()
            # Clear approved_at if status changes from approved to something else
            elif obj.status != "approved" and obj.approved_at:
                obj.approved_at = None
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            if hasattr(e, "message_dict"):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            else:
                messages.error(request, str(e))
            raise

    actions = ["approve_applications"]

    def approve_applications(self, request, queryset):
        updated = queryset.update(
            status="approved",
            approved_at=timezone.now(),
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f"{updated} applications approved successfully.")

    approve_applications.short_description = "Approve selected applications"
