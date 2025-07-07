from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render

from accounts.forms import AccountForm, CombinedRegistrationForm
from accounts.models import Account


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
                    "Registration and application submitted successfully! Please wait for approval.",
                )
                return HttpResponse(status=201)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = CombinedRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def account_form(request):
    # Check if user already has an account
    existing_account = Account.objects.filter(user=request.user).first()

    if existing_account and existing_account.status == "approved":
        return redirect("congratulations")

    if request.method == "POST":
        form = AccountForm(request.POST, request.FILES, instance=existing_account)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.user = request.user
                application.save()
                messages.success(request, "Application submitted successfully!")
                return redirect("application_status")
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = AccountForm(instance=existing_account)

    return render(
        request,
        "accounts/account_form.html",
        {"form": form, "existing_account": existing_account},
    )
