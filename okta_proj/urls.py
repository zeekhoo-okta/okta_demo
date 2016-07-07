"""okta_proj URL Configuration
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import logout
from .views import LoginView, RegistrationView, registration_success, message_no_saml
from django.views.generic import TemplateView


urlpatterns = [
    # home
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),

    # admin page
    url(r'^admin/', admin.site.urls, name='django_admin'),

    # Login and logout views
    url(r'^login/$', LoginView, name='login_user'),
    url(r'^logout/$', logout, name='logout_user'),

    # Registration
    url(r'^register/$', RegistrationView, name='register_user'),
    url(r'^register/success/$', registration_success, name='registration_success'),

    # App message
    url(r'^login/message/$', message_no_saml, name='message_no_saml'),
]
