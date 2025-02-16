from django.shortcuts import redirect, render

from resources.froms import EventForm


def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()  # Save the event in the database
            referer = request.session.get('referer', 'timetable-index')  # Use session variable for referer
            return redirect(referer)
    else:
        request.session['referer'] = request.META.get('HTTP_REFERER', 'event-list')  # Store referer in session
        form = EventForm()

    return render(request, 'resources/add_event.html', {'form': form})
