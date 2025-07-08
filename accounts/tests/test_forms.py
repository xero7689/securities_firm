import pytest

from accounts.forms import AccountForm, CombinedRegistrationForm


@pytest.mark.django_db
def test_valid_account_form():
    form_data = {
        "phone_number": "123-456-7890",
        "address": "123 Test St, Test City, TC 12345",
    }
    form = AccountForm(data=form_data)
    assert form.is_valid()


def test_invalid_phone_number():
    form_data = {"phone_number": "invalid-phone", "address": "123 Test St"}
    form = AccountForm(data=form_data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_valid_combined_registration_form():
    form_data = {
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password1": "testpassword123",
        "password2": "testpassword123",
        "phone_number": "123-456-7890",
        "address": "123 Test St, Test City, TC 12345",
    }
    form = CombinedRegistrationForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_combined_registration_form_invalid_phone():
    form_data = {
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password1": "testpassword123",
        "password2": "testpassword123",
        "phone_number": "invalid-phone",
        "address": "123 Test St, Test City, TC 12345",
    }
    form = CombinedRegistrationForm(data=form_data)
    assert not form.is_valid()
    assert "phone_number" in form.errors


@pytest.mark.django_db
def test_combined_registration_form_missing_required_fields():
    form_data = {
        "username": "testuser",
        "password1": "testpassword123",
        "password2": "testpassword123",
    }
    form = CombinedRegistrationForm(data=form_data)
    assert not form.is_valid()
    assert "email" in form.errors
    assert "first_name" in form.errors
    assert "last_name" in form.errors
    assert "phone_number" in form.errors
    assert "address" in form.errors


@pytest.mark.django_db
def test_combined_registration_form_password_mismatch():
    form_data = {
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password1": "testpassword123",
        "password2": "differentpassword",
        "phone_number": "123-456-7890",
        "address": "123 Test St, Test City, TC 12345",
    }
    form = CombinedRegistrationForm(data=form_data)
    assert not form.is_valid()
    assert "password2" in form.errors


@pytest.mark.django_db
def test_combined_registration_form_save():
    form_data = {
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password1": "testpassword123",
        "password2": "testpassword123",
        "phone_number": "123-456-7890",
        "address": "123 Test St, Test City, TC 12345",
    }
    form = CombinedRegistrationForm(data=form_data)
    assert form.is_valid()

    user = form.save(commit=False)
    assert user.username == "testuser"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.email == "test@example.com"
