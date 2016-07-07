"""okta_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
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

    # Message
    url(r'^login/message/$', message_no_saml, name='message_no_saml'),
]
