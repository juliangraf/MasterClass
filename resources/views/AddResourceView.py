from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import FormView

from resources.froms import ResourceForm
from resources.models import Role


def add_resource(request, role_id):
    role = Role.objects.get(id=role_id)
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            # Save the new resource
            resource = form.save(commit=False)
            resource.role = role
            resource.save()

            # Redirect to a specific page, for example, the timetable view
            return HttpResponseRedirect(reverse('timetable-all', args=[role.id]))
    else:
        form = ResourceForm()

    return render(request, 'resources/add_resource.html', {'form': form, 'role': role})


class AddResourceView(FormView):
    template_name = 'resources/add_resource.html'
    form_class = ResourceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = get_object_or_404(Role, id=self.kwargs['role'])
        return context

    def form_valid(self, form):
        role = get_object_or_404(Role, id=self.kwargs['role'])
        resource = form.save(commit=False)
        resource.role = role
        resource.save()
        form.save_m2m()  # Speichert ManyToMany-Beziehungen
        return redirect('/')
