import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import Account

User = get_user_model()


@pytest.mark.django_db
def test_account_creation(user):
    account = Account.objects.create(
        user=user,
        phone_number="123-456-7890",
        address="123 Test St",
        status="pending",
    )
    assert account.status == "pending"
    assert str(account) == "testuser - Pending"


@pytest.mark.django_db
def test_account_status_choices(user):
    account = Account.objects.create(
        user=user, phone_number="123-456-7890", address="123 Test St"
    )

    # Test pending and approved statuses
    statuses = ["pending", "approved"]
    for status in statuses:
        account.status = status
        account.save()
        assert account.status == status

    # Test rejected status with required reason
    account.status = "rejected"
    account.rejection_reason = ""
    with pytest.raises(ValidationError):
        account.save()

    account.rejection_reason = "Test reject reason"
    account.save()
    assert account.status == "rejected"

    # Test additional docs required with reason
    account.status = "additional_docs_required"
    account.additional_docs_reason = ""
    with pytest.raises(ValidationError):
        account.save()

    account.additional_docs_reason = "Test additional docs reason"
    account.save()
    assert account.status == "additional_docs_required"


@pytest.mark.django_db
def test_reviewed_by_and_reviewed_at_fields(user):
    reviewer = User.objects.create_user(
        username="reviewer", email="reviewer@example.com", password="reviewpass123"
    )
    application = Account.objects.create(
        user=user,
        phone_number="123-456-7890",
        address="123 Test St",
        reviewed_by=reviewer,
        reviewed_at=timezone.now(),
    )
    assert application.reviewed_by == reviewer
    assert application.reviewed_at is not None


@pytest.mark.django_db
def test_reviewed_by_can_be_null(user):
    application = Account.objects.create(
        user=user, phone_number="123-456-7890", address="123 Test St"
    )
    assert application.reviewed_by is None
    assert application.reviewed_at is None
