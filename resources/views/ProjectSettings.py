from django.shortcuts import render, redirect

from resources.froms import ProjectForm
from resources.models import Project

def project_settings(request):
    project = Project.objects.first()

    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("timetable-index")

    return render(request, "resources/project_settings.html", {"form": form})
