from datetime import datetime, timedelta, timezone
from math import floor

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import *

from resources.models import *


class Timetable2(TemplateView):
    template_name = 'resources/timetable2.html'

    def view_event(self, event, exclude):
        flatten = lambda l: [item for sublist in l for item in sublist]

        related = flatten([d.descendants() for d in event.dependencies.exclude(id__in=exclude)])
        roles = set(r.role for r in related)

        dependencies = [{
            'role': role.label,
            'resources': [r for r in related if r.role.id == role.id],
        } for role in sorted(roles, key=lambda x: x.weight)]

        return {
            'start': event.start,
            'end': event.end,
            'label': event.label,
            'dependencies': dependencies,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # global flag: whether to display events with is_global==true
        show_globals = bool(int(self.request.GET.get('show_globals', 1)))
        from_date = self.request.GET.get('start', None)
        to_date = self.request.GET.get('end', None)

        # case 1: single resource
        if ('resource' in self.kwargs):
            resources = [get_object_or_404(Resource, pk=self.kwargs['resource'])]

        # case 2: all resources for specific role
        elif ('role' in self.kwargs):
            role = get_object_or_404(Role, pk=self.kwargs['role']);
            resources = list(Resource.objects.filter(role=role))

        else:
            # TODO throw 404
            resources = []

        context['timetables'] = []

        for resource in resources:
            related_resources = resource.ancestors()
            descendants = resource.descendants()

            events = self.get_events(
                related_resources,
                show_globals=show_globals,
                from_date=from_date,
                to_date=to_date)
            dates = set(map(lambda x: x.start.date(), events))

            events_by_day = []
            for date in sorted(dates):
                events_by_day.append({
                    'date': date,
                    'events': [self.view_event(event, exclude=[r.id for r in descendants]) for event in events if
                               event.start.date() == date]
                })

            start_time = datetime.strptime("08:00", "%H:%M").replace(tzinfo=timezone.utc)
            end_time = datetime.strptime("20:00", "%H:%M").replace(tzinfo=timezone.utc)
            interval_minutes = 15
            time_slots = generate_time_slots(start_time, end_time, interval_minutes)

            events_by_timeslot = []
            days = [x['date'] for x in events_by_day]

            for time_slot in time_slots:
                events_in_timeslot = []
                for day in days:
                    events_on_day_by_timeslot = []
                    for event in events:
                        event_start = event.start
                        event_end = event.end

                        if (event_start.date() == day and time_slot['time'].time() <= event_start.time() <
                                (time_slot['time'] + timedelta(minutes=15)).time()):
                            duration_minutes = (event_end - event_start).total_seconds() / 60
                            width_percentage = (duration_minutes / interval_minutes)  # * 100
                            events_on_day_by_timeslot = {'label': event.label,
                                                         'start': event.start,
                                                         'end': event.end,
                                                         'colspan': max(floor(width_percentage), 1), }
                    events_in_timeslot.append({'day': day,
                                               'event': events_on_day_by_timeslot})
                events_by_timeslot.append({'timeslot': time_slot,
                                           'days': events_in_timeslot})

            timetable = {
                'resource': resource,
                'descendants': descendants,
                'events_by_day': events_by_day,
                'time_slots': time_slots,
                'events_by_timeslot': events_by_timeslot,
            }

            context['timetables'].append(timetable)

        return context

    def get_events(self, resources, show_globals, from_date, to_date):
        query = Event.objects
        if show_globals:
            query = query.filter(
                Q(is_global=True) | Q(dependencies__in=resources)
            )
        else:
            query = query.filter(dependencies__in=resources)
        if (from_date): query = query.filter(end__gt=from_date)
        if (to_date):   query = query.filter(start__lt=to_date)

        return list(query.order_by('start'))


def generate_time_slots(start_time, end_time, interval_minutes):
    time_slots = []
    current_time = start_time
    while current_time < end_time:
        if current_time.time().minute == 0:
            time_slots.append({'time': current_time, 'str': current_time.strftime("%H:%M")})
        else:
            time_slots.append({'time': current_time, 'str': ""})
        current_time += timedelta(minutes=interval_minutes)
    return time_slots
