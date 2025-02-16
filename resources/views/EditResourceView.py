from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from resources.froms import ResourceForm
from resources.models import Resource


def update_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)

    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            resource = form.save(commit=False)  # Speichert noch nicht in die DB
            resource.save()  # Speichert das Objekt in die DB, aber ohne ManyToMany-Felder
            form.save_m2m()  # Speichert die ManyToMany-Beziehungen
            return redirect(reverse('timetable-index', args=[]))  # Stelle sicher, dass diese URL existiert
    else:
        form = ResourceForm(instance=resource)  # Bestehende Werte setzen

    return render(request, 'resources/edit_resource.html', {'form': form, 'resource': resource})


def delete_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    resource.delete()
    return redirect('timetable-index')
