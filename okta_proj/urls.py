"""okta_proj URL Configuration
"""
from django.conf.urls import url
from django.contrib import admin
from .views import LoginView, SecondFAView, RegistrationView, registration_success, dashboard, logout, verify
from django.views.generic import TemplateView


urlpatterns = [
    # home
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),

    # admin page
    url(r'^admin/', admin.site.urls, name='django_admin'),

    # Login and logout views
    url(r'^login/$', LoginView, name='login_user'),
    url(r'^login/second-fa/$', SecondFAView, name='second_fa'),
    url(r'^logout/$', logout, name='logout_user'),

    # Registration
    url(r'^register/$', RegistrationView, name='register_user'),
    url(r'^register/success/$', registration_success, name='registration_success'),

    # user logged in
    url(r'^dashboard/$', dashboard, name='dashboard'),

    #  verify 2fa
    url(r'^login/second-fa/verify/(?P<p>[a-zA-Z0-9]+)/$', verify, name='verify'),

]
