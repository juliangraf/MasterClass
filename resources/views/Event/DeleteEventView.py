from django.shortcuts import get_object_or_404, redirect

from resources.models import Event


def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        event.delete()
        return redirect("timetable-index")
    return None