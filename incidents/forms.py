from django import forms
from django.forms import inlineformset_factory
from .models import Incident, HazardImage


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'title', 'description', 'incident_type', 'status',
            'latitude', 'longitude', 'location_description',
            'assigned_to', 'priority', 'related_hazards'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Incident Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detailed description of the incident'
            }),
            'incident_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001'
            }),
            'location_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Describe the location'
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control'}),
            'related_hazards': forms.CheckboxSelectMultiple(),
        }


class HazardImageForm(forms.ModelForm):
    class Meta:
        model = HazardImage
        fields = ['image', 'description']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image description'
            }),
        }


# Inline formset for HazardImages within Incident
HazardImageFormSet = inlineformset_factory(
    Incident,
    HazardImage,
    form=HazardImageForm,
    extra=1,
    can_delete=True
)


class IncidentFilterForm(forms.Form):
    """Form for advanced filtering on the dashboard"""
    incident_type = forms.MultipleChoiceField(
        choices=Incident._meta.get_field('incident_type').choices,
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    status = forms.MultipleChoiceField(
        choices=Incident._meta.get_field('status').choices,
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    priority_min = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min'
        })
    )
    priority_max = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max'
        })
    )
    date_from = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    date_to = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title or location'
        })
    )
