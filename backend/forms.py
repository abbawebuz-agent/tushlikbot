from django import forms

from .models import Lead


class LeadForm(forms.ModelForm):
    # Honeypot field: must stay empty (basic anti-bot)
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Lead
        fields = ["contact_name", "phone"]
        widgets = {
            "contact_name": forms.TextInput(attrs={"placeholder": "Например: Алишер"}),
            "phone": forms.TextInput(attrs={"placeholder": "+998 90 123 45 67"}),
        }

    def clean(self):
        cleaned = super().clean()
        if (cleaned.get("website") or "").strip():
            raise forms.ValidationError("Invalid submission.")
        return cleaned

