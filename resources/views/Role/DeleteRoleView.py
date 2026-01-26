from django.shortcuts import get_object_or_404, redirect

from resources.models import Role


def delete_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    role.delete()
    return redirect('timetable-index')
