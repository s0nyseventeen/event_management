from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from events.views import EventRegistrationView
from events.views import EventSearch
from events.views import EventViewSet
from events.views import Login
from events.views import Logout
from events.views import Registration

router = DefaultRouter()
router.register('events', EventViewSet)

urlpatterns = [
    path('events/search/', EventSearch.as_view(), name='search-event'),
    path('', include(router.urls)),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('register/', Registration.as_view(), name='register'),
    path(
        'events/<int:event_id>/register/',
        EventRegistrationView.as_view(),
        name='register-event'
    ),
]
