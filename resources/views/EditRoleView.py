from django.shortcuts import get_object_or_404, redirect, render

from resources.froms import ResourceForm, RoleForm
from resources.models import Resource, Role


def update_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)

    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save(commit=False)  # Speichert noch nicht in die DB
            role.save()  # Speichert das Objekt in die DB, aber ohne ManyToMany-Felder
            form.save_m2m()  # Speichert die ManyToMany-Beziehungen
            referer = request.session.get('referer', 'timetable-index')  # Use session variable for referer
            return redirect(referer)
    else:
        request.session['referer'] = request.META.get('HTTP_REFERER', 'event-list')  # Store referer in session
        form = RoleForm(instance=role)  # Bestehende Werte setzen

    return render(request, 'resources/edit_role.html', {'form': form, 'role': role})


def delete_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    role.delete()
    return redirect('timetable-index')
