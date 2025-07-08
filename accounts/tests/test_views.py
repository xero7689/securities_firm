import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from accounts.models import Account


@pytest.mark.django_db
def test_register_view_get(client):
    response = client.get(reverse("register"))
    assert response.status_code == 200
    assert "Create Account" in response.content.decode()


@pytest.mark.django_db
def test_register_view_post(client):
    form_data = {
        "username": "newuser",
        "first_name": "New",
        "last_name": "User",
        "email": "newuser@example.com",
        "password1": "newpass123",
        "password2": "newpass123",
        "phone_number": "123-456-7890",
        "address": "123 Test St",
    }
    response = client.post(reverse("register"), data=form_data)
    assert response.status_code == 302  # Redirect after successful registration
    assert User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_login_required_for_account_form(client):
    response = client.get(reverse("account_form"))
    assert response.status_code == 302  # Redirect to login


@pytest.mark.django_db
def test_account_form_authenticated(client, user):
    client.login(username="testuser", password="testpass123")
    response = client.get(reverse("account_form"))
    assert response.status_code == 200
    assert "Securities Account" in response.content.decode()


@pytest.mark.django_db
def test_account_status_requires_account(client, user):
    client.login(username="testuser", password="testpass123")
    response = client.get(reverse("account_status"))
    assert response.status_code == 404  # No account exists


@pytest.mark.django_db
def test_account_status_with_account(client, user):
    client.login(username="testuser", password="testpass123")
    Account.objects.create(
        user=user, phone_number="123-456-7890", address="123 Test St"
    )
    response = client.get(reverse("account_status"))
    assert response.status_code == 200
    assert "Account Status" in response.content.decode()


@pytest.mark.django_db
def test_congratulations_requires_approved_account(client, user):
    client.login(username="testuser", password="testpass123")
    # Create pending account
    Account.objects.create(
        user=user,
        phone_number="123-456-7890",
        address="123 Test St",
        status="pending",
    )
    response = client.get(reverse("congratulations"))
    assert response.status_code == 404  # Account not approved


@pytest.mark.django_db
def test_congratulations_with_approved_account(client, user):
    client.login(username="testuser", password="testpass123")
    Account.objects.create(
        user=user,
        phone_number="123-456-7890",
        address="123 Test St",
        status="approved",
        approved_at=timezone.now(),
    )
    response = client.get(reverse("congratulations"))
    assert response.status_code == 200
    assert "Congratulations" in response.content.decode()


@pytest.mark.django_db
def test_admin_can_access_account_admin(client, admin_user):
    client.login(username="admin", password="adminpass123")
    response = client.get("/admin/accounts/account/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_can_change_account_status(client, admin_user, regular_user, account):
    client.login(username="admin", password="adminpass123")
    client.post(
        f"/admin/accounts/account/{account.id}/change/",
        {
            "user": regular_user.id,
            "phone_number": "123-456-7890",
            "address": "123 Test St",
            "status": "approved",
            "rejection_reason": "",
            "additional_docs_reason": "",
        },
    )
    account.refresh_from_db()
    assert account.status == "approved"
    assert account.approved_at is not None
    assert account.reviewed_by == admin_user
    assert account.reviewed_at is not None


@pytest.mark.django_db
def test_admin_bulk_approve_sets_reviewer_fields(
    client, admin_user, regular_user, account
):
    # Create additional accounts for bulk testing
    user2 = User.objects.create_user(
        username="testuser2", email="test2@example.com", password="testpass123"
    )
    app2 = Account.objects.create(
        user=user2, phone_number="123-456-7891", address="456 Test St"
    )

    client.login(username="admin", password="adminpass123")
    client.post(
        "/admin/accounts/account/",
        {
            "action": "approve_accounts",
            "_selected_action": [account.id, app2.id],
        },
    )

    account.refresh_from_db()
    app2.refresh_from_db()

    assert account.status == "approved"
    assert account.reviewed_by == admin_user
    assert account.reviewed_at is not None

    assert app2.status == "approved"
    assert app2.reviewed_by == admin_user
    assert app2.reviewed_at is not None
