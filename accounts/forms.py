from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import ProviderProfile, User


class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Role.choices)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "e.g. janedoe"}
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "you@example.com"}
        )
        self.fields["role"].widget.attrs.update({"class": "form-select"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

        self.fields["role"].help_text = "Choose Customer to book services, or Provider to offer services."
        self.fields["email"].help_text = "Used for booking updates and notifications."


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "avatar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if name == "avatar":
                continue
            f.widget.attrs.update({"class": "form-control"})
        self.fields["avatar"].widget.attrs.update({"class": "form-control"})


class ProviderProfileForm(forms.ModelForm):
    class Meta:
        model = ProviderProfile
        fields = (
            "display_name",
            "phone",
            "whatsapp_number",
            "instagram",
            "snapchat",
            "tiktok",
            "available_from",
            "available_to",
            "bio",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["display_name"].widget.attrs.update({"class": "form-control"})
        self.fields["phone"].widget.attrs.update({"class": "form-control"})
        self.fields["whatsapp_number"].widget.attrs.update({"class": "form-control", "placeholder": "23324xxxxxxx"})
        self.fields["instagram"].widget.attrs.update({"class": "form-control", "placeholder": "username"})
        self.fields["snapchat"].widget.attrs.update({"class": "form-control", "placeholder": "username"})
        self.fields["tiktok"].widget.attrs.update({"class": "form-control", "placeholder": "username"})
        self.fields["available_from"].widget = forms.TimeInput(attrs={"type": "time", "class": "form-control"})
        self.fields["available_to"].widget = forms.TimeInput(attrs={"type": "time", "class": "form-control"})
        self.fields["bio"].widget.attrs.update({"class": "form-control", "rows": 3})

