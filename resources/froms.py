from django import forms

from .models import Resource, Event


class ResourceForm(forms.ModelForm):
    dependencies = forms.ModelMultipleChoiceField(queryset=Resource.objects.all(),  # Alle Ressourcen als Auswahl
                                                  widget=forms.CheckboxSelectMultiple,  # Checkboxes für Mehrfachauswahl
                                                  required=False  # Damit keine Auswahl erzwungen wird
                                                  )

    class Meta:
        model = Resource
        fields = ['label', 'description', 'dependencies']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['label', 'start', 'end', 'is_global', 'dependencies']
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'dependencies': forms.CheckboxSelectMultiple,  # Use checkbox for dependencies selection
        }
