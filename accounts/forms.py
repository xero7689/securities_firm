from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CombinedRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    # Account fields
    phone_number = forms.CharField(max_length=20, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if phone:
            # Basic phone number validation
            if (
                not phone.replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
                .replace("+", "")
                .isdigit()
            ):
                raise ValidationError("Please enter a valid phone number")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
