from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.translation import gettext_lazy as _

from .models import *
from .models import Event


class ResourceAdmin(admin.ModelAdmin):
    # Display resources in a table format with columns for 'label', 'role', and 'description'
    list_display = ('label', 'role', 'description')

    # Add filtering option by role in the sidebar
    list_filter = ('role',)

    # Add ordering of resources first by 'role' and then by 'label'
    ordering = ('role', 'label')

    # Group resources by 'role' in the list view
    fieldsets = (
        (None, {
            'fields': ('label', 'description', 'role', 'dependencies')
        }),
    )

    # Use filter_horizontal to make selecting dependencies easier
    filter_horizontal = ('dependencies',)

    # Optional: Add search functionality to make finding resources easier
    search_fields = ('label', 'description')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('lorem/', self.admin_site.admin_view(self.test_view))
        ]
        return my_urls + urls

    def test_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
        )
        return TemplateResponse(request, "resources/lorem.html", context)


class DependencyCountFilter(admin.SimpleListFilter):
    # Define the title and parameter for the filter
    title = _('number of dependencies')
    parameter_name = 'dependency_count'

    def lookups(self, request, model_admin):
        # Generate filter options for 0-10 dependencies and "11 or more"
        options = [(str(i), _(f'{i} dependency{"" if i == 1 else "ies"}')) for i in range(11)]
        options.append(('11+', _('11 or more dependencies')))
        return options

    def queryset(self, request, queryset):
        # Get the filter value from the URL
        value = self.value()
        if value:
            if value == '11+':
                return queryset.annotate(num_dependencies=Count('dependencies')).filter(num_dependencies__gte=11)
            else:
                # Convert the value to an integer and filter by that number of dependencies
                num_dependencies = int(value)
                return queryset.annotate(num_dependencies=Count('dependencies')).filter(
                    num_dependencies=num_dependencies)
        return queryset


class EventAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_global', 'get_dependency_count', 'dependency_labels')
    list_filter = ('is_global', DependencyCountFilter)
    search_fields = ('label',)

    # Use filter_horizontal for dependencies to make selection easier
    filter_horizontal = ('dependencies',)

    # Method to display a list of dependencies as a string
    def dependency_labels(self, obj):
        return ', '.join([str(resource) for resource in obj.dependencies.all()])

    dependency_labels.short_description = 'Dependencies'

    def get_dependency_count(self, obj):
        return obj.dependencies.count()  # Count the number of dependencies for the event

    get_dependency_count.short_description = 'Number of Dependencies'  # Set a custom column name in the list view

    def response_change(self, request, obj):
        """ if user clicked edit link in calendar, return back to calendar view """
        response = super(EventAdmin, self).response_change(request, obj)

        print("response_change")
        if (isinstance(response, HttpResponseRedirect) and
                #                response['location'] == '../' and
                request.GET.get('source') == 'calendar'):
            role = request.GET.get('role')
            response['location'] = reverse('calendar', args=(role,))

        return response


admin.site.register(Role)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Project)
