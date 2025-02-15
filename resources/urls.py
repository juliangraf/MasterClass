from django.urls import path

from .views import *
from .views.AddResourceView import AddResourceView

urlpatterns = [
    path('', TimetableIndex.as_view(), name='timetable-index'),
    path('timetable/', TimetableIndex.as_view(), name='timetable-index'),
    path('timetable/<int:resource>', Timetable.as_view(), name='timetable'),
    path('timetable/role/<int:role>', Timetable.as_view(), name='timetable-all'),
    path('calendar/<int:role>', CalendarView.as_view(), name='calendar'),
    path('conflicts/<int:resource>', ConflictList.as_view()),
    path('add/<int:role>/', AddResourceView.as_view(), name='add-resource'),

    path('resource/<int:pk>', ResourceView.as_view(), name="resource"),
    path('resource/<int:pk>/dependency/<int:dependency>', ResourceDependenciesView.as_view(),
         name='resource-dependency'),

    path('json/events/', EventsJSON.as_view(), name='events-json'),
    path('json/events/<int:role>', EventsJSON.as_view(), name='events-by-role-json'),
    path('json/resources/<int:role>', ResourcesJSON.as_view(), name='resources-by-role-json'),
    path('json/resources/', ResourcesJSON.as_view(), name='resources-json'),
    path('json/conflicts/', ConflictsJSON.as_view(), name='conflicts-json'),
]
