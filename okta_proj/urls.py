"""okta_proj URL Configuration
"""
from django.conf.urls import url
from django.contrib import admin
from .views import view_home, LoginView, SecondFAView, RegistrationView, ActivationView, \
    registration_success, dashboard, intranet, logout, session, verify
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    # home
    url(r'^$', view_home, name='home'),

    # admin page
    url(r'^admin/', admin.site.urls, name='django_admin'),

    # Login and logout views
    url(r'^login/$', LoginView, name='login_user'),
    url(r'^login/second-fa/$', SecondFAView, name='second_fa'),
    url(r'^logout/$', logout, name='logout_user'),
    url(r'^session/$', session, name='session'),

    # Registration
    url(r'^register/$', RegistrationView, name='register_user'),
    url(r'^register/success/$', registration_success, name='registration_success'),
    url(r'^activate/([a-zA-Z0-9]+)/$', ActivationView, name='activate_user'),

    # user logged in
    url(r'^dashboard/$', dashboard, name='dashboard'),
    url(r'^intranet/$', intranet, name='intranet'),

    #  verify 2fa
    url(r'^login/second-fa/verify/(?P<p>[a-zA-Z0-9]+)/$', verify, name='verify'),

]
urlpatterns += staticfiles_urlpatterns()
