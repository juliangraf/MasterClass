from django.shortcuts import get_object_or_404, redirect, render

from resources.froms import EventForm
from resources.models import Event


def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            event.save()  # Save the event
            form.save_m2m()  # Save ManyToMany relationships
            referer = request.session.get('referer', 'timetable-index')  # Use session variable for referer
            return redirect(referer)
    else:
        request.session['referer'] = request.META.get('HTTP_REFERER', 'event-list')  # Store referer in session
        form = EventForm(instance=event)  # Prefill the form with the event data

    return render(request, 'resources/edit_event.html', {'form': form, 'event': event})
