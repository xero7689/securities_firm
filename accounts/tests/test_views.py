import pytest

from accounts.models import Account


@pytest.mark.django_db
def test_application_creation(user):
    application = Account.objects.create(
        user=user,
        phone_number="123-456-7890",
        address="123 Test St",
        status="pending",
    )
    assert application.status == "pending"
    assert str(application) == "testuser - Pending"
