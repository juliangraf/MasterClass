from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import *

from resources.models import *


class CalendarView(ListView):
    template_name = 'resources/calendar.html'
    model = Resource
    context_object_name = 'resources'

    def get_queryset(self):
        role_pk = self.kwargs.get('role')
        if role_pk:
            primary_role = get_object_or_404(Role, pk=role_pk)
        else:
            primary_role = Role.objects.first()
            if not primary_role:
                return Resource.objects.none()
        return Resource.objects.exclude(role=primary_role.id).order_by('role')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role_pk = self.kwargs.get('role')
        if role_pk:
            primary_role = get_object_or_404(Role, pk=role_pk)
        else:
            primary_role = Role.objects.first()
            if not primary_role:
                return Resource.objects.none()
        context['primary_role'] = primary_role
        context['roles'] = Role.objects.all()
        context['project'] = Project.objects.get(pk=1)
        return context

    def post(self, request, *args, **kwargs):
        if ('id' in request.POST) and request.POST['id']:
            event = get_object_or_404(Event, pk=request.POST['id'])

            if ('start' in request.POST):
                event.start = request.POST['start']
            if ('end' in request.POST):
                event.end = request.POST['end']
        else:
            event = Event.objects.create(start=request.POST['start'], end=request.POST['end'])

        if ('is_global' in request.POST):
            event.is_global = request.POST['is_global']

        if ('removeResource' in request.POST):
            id = request.POST['removeResource']
            event.dependencies.remove(id)

        if ('resourceIds' in request.POST):
            dependencies = map(int, request.POST['resourceIds'].split(','))
            for id in dependencies: event.dependencies.add(id)

        # TODO allow changing primary resource

        event.save()
        return HttpResponse()
