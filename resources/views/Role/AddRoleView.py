from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import FormView

from resources.froms import ResourceForm, RoleForm
from resources.models import Role


def add_role(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            # Save the new resource
            resource = form.save(commit=False)
            resource.save()
            referer = request.session.get('referer', 'timetable-index')  # Use session variable for referer
            return redirect(referer)
    else:
        request.session['referer'] = request.META.get('HTTP_REFERER', 'event-list')  # Store referer in session
        form = RoleForm()

    return render(request, 'resources/add_role.html', {'form': form})
