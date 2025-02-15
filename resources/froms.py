from django import forms

from .models import Resource


class ResourceForm(forms.ModelForm):
    dependencies = forms.ModelMultipleChoiceField(queryset=Resource.objects.all(),  # Alle Ressourcen als Auswahl
        widget=forms.CheckboxSelectMultiple,  # Checkboxes für Mehrfachauswahl
        required=False  # Damit keine Auswahl erzwungen wird
    )

    class Meta:
        model = Resource
        fields = ['label', 'description', 'dependencies']
