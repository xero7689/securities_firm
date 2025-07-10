from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render

from accounts.forms import AccountForm, CombinedRegistrationForm
from accounts.models import Account


def home(request):
    if request.user.is_authenticated:
        return redirect("account_status")
    return redirect("login")


def register(request):
    # Check if user is authenticated admin/staff without account
    if request.user.is_authenticated and (
        request.user.is_staff or request.user.is_superuser
    ):
        try:
            Account.objects.get(user=request.user)
        except Account.DoesNotExist:
            return redirect("admin_without_account")

    if request.method == "POST":
        form = CombinedRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the user
                with transaction.atomic():
                    # Create Django User
                    user = form.save()

                    # Create the Securities Account
                    _ = Account.objects.create(
                        user=user,
                        phone_number=form.cleaned_data["phone_number"],
                        address=form.cleaned_data["address"],
                    )

                # Log the user in
                login(request, user)
                messages.success(
                    request,
                    "Registration and account submitted successfully! Please wait for approval.",
                )
                return redirect("account_status")
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = CombinedRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def supplement_form(request):
    # Check if user already has an account
    existing_account = Account.objects.filter(user=request.user).first()

    # Check if user is admin/staff without account
    if not existing_account and (request.user.is_staff or request.user.is_superuser):
        return redirect("admin_without_account")

    if existing_account and existing_account.status == "approved":
        return redirect("congratulations")

    # Prevent access for rejected accounts
    if existing_account and existing_account.status == "rejected":
        messages.error(
            request,
            "Your account has been rejected. You cannot submit additional documents.",
        )
        return redirect("account_status")

    # Prevent access for pending accounts
    if existing_account and existing_account.status == "pending":
        messages.error(
            request,
            "Your account is currently under review. You cannot submit additional documents.",
        )
        return redirect("account_status")

    if request.method == "POST":
        form = AccountForm(request.POST, request.FILES, instance=existing_account)
        if form.is_valid():
            try:
                account = form.save(commit=False)
                account.user = request.user
                account.save()
                messages.success(request, "account submitted successfully!")
                return redirect("account_status")
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = AccountForm(instance=existing_account)

    return render(
        request,
        "accounts/account_form.html",
        {"form": form, "existing_account": existing_account},
    )


@login_required
def account_status(request):
    try:
        account = Account.objects.get(user=request.user)
    except Account.DoesNotExist:
        # Check if user is admin/staff without account
        if request.user.is_staff or request.user.is_superuser:
            return redirect("admin_without_account")
        # Regular user without account should not happen, but redirect to register
        return redirect("register")

    # Automatically redirect approved users to congratulations page
    if account.status == "approved":
        return redirect("congratulations")

    context = {"account": account, "status_info": get_status_info(account)}

    return render(request, "accounts/account_status.html", context)


@login_required
def admin_without_account(request):
    """View for admin users who don't have an Account instance"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect("account_status")

    return render(request, "accounts/admin_without_account.html")


@login_required
def congratulations(request):
    try:
        account = Account.objects.get(user=request.user)
    except Account.DoesNotExist:
        # Check if user is admin/staff without account
        if request.user.is_staff or request.user.is_superuser:
            return redirect("admin_without_account")
        return redirect("account_status")

    if account.status == "approved":
        return render(request, "accounts/congratulations.html", {"account": account})
    else:
        return redirect("account_status")


def get_status_info(account):
    """Returns status-specific information for display"""
    status_info = {
        "pending": {
            "title": "account Pending",
            "message": f"Your account was submitted on {account.created_at.strftime('%B %d, %Y at %I:%M %p')}. Please wait for review.",
            "icon": "clock",
            "color": "warning",
        },
        "approved": {
            "title": "Account Approved",
            "message": f"Congratulations! Your account was approved on {account.approved_at.strftime('%B %d, %Y at %I:%M %p') if account.approved_at else 'N/A'}.",
            "icon": "check-circle",
            "color": "success",
        },
        "rejected": {
            "title": "account Rejected",
            "message": f"Your account was rejected. Reason: {account.rejection_reason or 'No specific reason provided'}"
            + (
                f" (Reviewed by {account.reviewed_by.get_full_name() or account.reviewed_by.username})"
                if account.reviewed_by
                else ""
            ),
            "icon": "x-circle",
            "color": "danger",
        },
        "additional_docs_required": {
            "title": "Additional Documents Required",
            "message": f"Please provide additional information: {account.additional_docs_reason or 'Please contact support for details'}"
            + (
                f" (Reviewed by {account.reviewed_by.get_full_name() or account.reviewed_by.username})"
                if account.reviewed_by
                else ""
            ),
            "icon": "file-text",
            "color": "info",
        },
    }

    return status_info.get(account.status, status_info["pending"])
