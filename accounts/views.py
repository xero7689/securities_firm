from django.contrib import messages
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponse

from accounts.models import Account
from accounts.forms import CombinedRegistrationForm


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
