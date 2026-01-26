from django.shortcuts import get_object_or_404, redirect

from resources.models import Resource


def delete_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    resource.delete()
    return redirect('timetable-index')