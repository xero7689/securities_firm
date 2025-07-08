from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import AccountForm, CombinedRegistrationForm
from accounts.models import Account


def home(request):
    if request.user.is_authenticated:
        return redirect("account_status")
    return redirect("login")


def register(request):
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

    if existing_account and existing_account.status == "approved":
        return redirect("congratulations")

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
    account = get_object_or_404(Account, user=request.user)

    context = {"account": account, "status_info": get_status_info(account)}

    return render(request, "accounts/account_status.html", context)


@login_required
def congratulations(request):
    account = get_object_or_404(Account, user=request.user, status="approved")
    return render(request, "accounts/congratulations.html", {"account": account})


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
