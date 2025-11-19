from django.shortcuts import render, redirect

from resources.froms import ProjectForm


def project_settings(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            referer = request.session.get('referer', 'timetable-index')  # Use session variable for referer
            return redirect(referer)
    else:
        form = ProjectForm()
    return render(request, "resources/project_settings.html", {"form": form})
