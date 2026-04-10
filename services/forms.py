from django import forms

from .models import AvailabilitySlot, Service, ServiceCategory


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ("category", "name", "description", "price", "image", "image_url", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = ServiceCategory.objects.order_by("name")
        self.fields["category"].widget.attrs.update({"class": "form-select"})
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["description"].widget.attrs.update({"class": "form-control", "rows": 4})
        self.fields["price"].widget.attrs.update({"class": "form-control"})
        self.fields["image_url"].widget.attrs.update(
            {"class": "form-control", "placeholder": "/static/images/services/example.jpg"}
        )


class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ("date", "time", "is_active")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }

