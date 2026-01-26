from django.conf.urls.static import static
from django.urls import path

from masterclass import settings
from .views import *
from resources.views.Event.AddEventView import add_event
from resources.views.Ressource.AddResourceView import AddResourceView
from resources.views.Role.AddRoleView import add_role
from resources.views.Event.EditEventView import update_event
from resources.views.Ressource.EditResourceView import update_resource
from resources.views.Role.EditRoleView import update_role
from .views.Event.DeleteEventView import delete_event
from .views.ProjectSettings import project_settings
from .views.Ressource.DeleteRessourceView import delete_resource
from .views.Role.DeleteRoleView import delete_role

urlpatterns = [
    path('', TimetableIndex.as_view(), name='timetable-home'),
    path('timetable/', TimetableIndex.as_view(), name='timetable-index'),
    path('timetable/<int:resource>', Timetable.as_view(), name='timetable'),
    path('timetable/role/<int:role>', Timetable.as_view(), name='timetable-all'),
    path('calendar/<int:role>', CalendarView.as_view(), name='calendar'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('calendar-settings/', project_settings, name='calendar-settings'),
    path('conflicts/', ConflictList.as_view(), name='conflicts'),
    path('resources/add/<int:role>/', AddResourceView.as_view(), name='add-resource'),
    path('role/add', add_role, name='add-role'),
    path('resources/edit/<int:resource_id>/', update_resource, name='update-resource'),
    path('role/edit/<int:role_id>/', update_role, name='update-role'),
    path('resources/delete/<int:resource_id>/', delete_resource, name='delete-resource'),
    path('role/delete/<int:role_id>/', delete_role, name='delete-role'),
    path('event/add/', add_event, name='add-event'),
    path('event/edit/<int:event_id>/', update_event, name='update-event'),
    path("events/<int:event_id>/delete/", delete_event, name="event-delete"),

    path('resource/<int:pk>', ResourceView.as_view(), name="resource"),
    path('resource/<int:pk>/dependency/<int:dependency>', ResourceDependenciesView.as_view(),
         name='resource-dependency'),

    path('json/events/', EventsJSON.as_view(), name='events-json'),
    path('json/events/<int:role>', EventsJSON.as_view(), name='events-by-role-json'),
    path('json/resources/<int:role>', ResourcesJSON.as_view(), name='resources-by-role-json'),
    path('json/resources/', ResourcesJSON.as_view(), name='resources-json'),
    path('json/conflicts/', ConflictsJSON.as_view(), name='conflicts-json'),
]

if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)