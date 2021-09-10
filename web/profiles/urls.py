from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views

from .views import (
    RegistrationView, LoginView, LogoutView,
    ProfileDetailView, ProfileUpdateView, ProfileChannelsGraphView, ProfileArgumentsView,
    ProfilePremisesView, ProfileFallaciesView
)


urlpatterns = [
    path('login/', LoginView.as_view(template_name="auth/login.html"), name='auth_login'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/profile', ProfileUpdateView.as_view(template_name="auth/update.html"), name='auth_profile_update'),
    path('register/', RegistrationView.as_view(template_name="auth/register.html"), name='auth_registration'),
    path('complete/', TemplateView.as_view(template_name="auth/complete.html"), name='auth_registration_complete'),
    path('users/<str:username>', ProfileDetailView.as_view(template_name="auth/profile.html"), name='auth_profile'),
    path('users/<str:username>/arguments', ProfileArgumentsView.as_view(), name='auth_profile_arguments'),
    path('users/<str:username>/premises', ProfilePremisesView.as_view(), name='auth_profile_premises'),
    path('users/<str:username>/fallacies', ProfileFallaciesView.as_view(), name='auth_profile_fallacies'),
    path('users/<str:username>/channels.json', ProfileChannelsGraphView.as_view(), name='auth_profile_channels'),
    path('password_reset/', views.PasswordResetView, {
            'template_name': 'auth/password_reset_form.html',
            'email_template_name': 'auth/password_reset_email.html'
        }, name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView,
        {
            'template_name': 'auth/password_reset_done.html'
        }, name='password_reset_done'),
    path('reset/<str:uidb64>/<str:token>/', views.PasswordResetConfirmView, {
            'template_name': 'auth/password_reset_confirm.html'
        }, name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView, {'template_name': 'auth/password_reset_complete.html'},
         name='password_reset_complete'),
]
