from django import forms

from services.models import Service

from .models import Booking


class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("date", "time", "contact_name", "contact_phone", "contact_email", "notes")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        }

    def __init__(self, *args, service: Service, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = service
        for fname in ["contact_name", "contact_phone", "contact_email"]:
            self.fields[fname].widget.attrs.update({"class": "form-control"})
        self.fields["notes"].widget.attrs.update({"class": "form-control", "rows": 3})

