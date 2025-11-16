from django.views.generic import ListView

from resources.models import Resource, Role


class TimetableIndex(ListView):
    template_name = 'resources/timetable_index.html'
    model = Resource

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resources = self.get_queryset().select_related('role')  # ensure role is prefetched
        all_roles = Role.objects.all()

        # Build list of (role, resources)
        roles_list = []
        for role in all_roles:
            role_resources = [r for r in resources if r.role == role]  # compare objects, not ids
            roles_list.append((role, role_resources))

        context['roles'] = roles_list
        context['active_page'] = 'stundenplan'
        return context
