import pytest
from django.contrib.auth.models import User

from accounts.models import Account


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass123"
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def account(regular_user):
    return Account.objects.create(
        user=regular_user, phone_number="123-456-7890", address="123 Test St"
    )
