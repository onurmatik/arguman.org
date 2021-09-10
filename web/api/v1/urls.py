from django.urls import path, include
from .users.views import profile_me


urlpatterns = [
    path(r'^auth/', include('api.v1.auth.urls')),
    path(r'^user/$', profile_me, name='api-me'),
    path(r'^users/', include('api.v1.users.urls')),
    path(r'^arguments/', include('api.v1.arguments.urls')),
    path(r'^newsfeed/', include('api.v1.newsfeed.urls')),
    path(r'^notifications/', include('api.v1.notifications.urls')),
]
