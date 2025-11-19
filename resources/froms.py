from django import forms

from .models import Resource, Event, Role


class ResourceForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4})
    )
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
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['label', 'plural_label']

