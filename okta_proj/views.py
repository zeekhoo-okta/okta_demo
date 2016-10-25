from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import serializers
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils.six import BytesIO
from django.http import HttpResponseRedirect, HttpResponse

#from django.views.decorators.csrf import csrf_protect

from okta import AuthClient, SessionsClient, UsersClient
from okta.framework.ApiClient import ApiClient
from okta.framework.Utils import Utils
from okta.models.session.Session import Session
from okta.models.user import User
from okta.models.user.LoginCredentials import LoginCredentials, Password
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from api.AuthClient2 import AuthClient2
from api.UsersResourceClient import UsersResourceClient
from okta_proj.api.models.session.UserSession import UserSession
from serializers.SessionSerializer import SessionSerializer
from .forms import LoginForm, RegistrationForm, mfaForm

OKTA_ORG = ''.join(['https://', settings.OKTA_ORG])
API_TOKEN = settings.OKTA_API_TOKEN


def view_home(request):
    if 'session' in request.session:
        return HttpResponseRedirect(reverse('dashboard'))

    return render(request, 'index.html')


def LoginView(request):
    c = None
    session = None
    if 'session' in request.session:
        session = _getSession(request.session['session'])

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)

        if form.is_valid():
            un = form.cleaned_data['username']
            pw = form.cleaned_data['password']

            try:
                # Create an auth client and post the username and password
                authCli = AuthClient2(OKTA_ORG, API_TOKEN)
                auth = authCli.authenticate(username=un, password=pw)
                status = auth.status
                print('status = {}'.format(status))

                if status == 'MFA_REQUIRED':
                    if auth.stateToken is not None and auth.embedded is not None:
                        mfa_factors = auth.embedded.factors
                        user = auth.embedded.user
                        s = UserSession(id='2fa_state', userId=user.id,
                                        login=user.profile.login,
                                        firstName=user.profile.firstName,
                                        lastName=user.profile.lastName,
                                        stateToken=auth.stateToken,
                                        factors=mfa_factors)

                        serializer = SessionSerializer(s)
                        json = JSONRenderer().render(serializer.data)
                        request.session['session'] = json

                        return HttpResponseRedirect(reverse('second_fa'))

                # If authentication is successful, exchange the session token for a session cookie
                if status == 'SUCCESS':
                    return _setCookieTokenAndLoadDash(request, auth.sessionToken)

            except Exception as oktaError:
                form.add_error(field=None, error=oktaError)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    c = {'dict': {'session': session, 'form': form}}
    return render(request, 'registration/login.html', c)


def _setCookieTokenAndLoadDash(request, session_token):
    sessionCli = SessionsClient(OKTA_ORG, API_TOKEN)
    session = sessionCli.create_session_by_session_token(session_token=session_token, additional_fields='cookieToken')

    redirect = ''.join(['http://', get_current_site(request).domain, reverse('dashboard')])

    postback = ''.join([OKTA_ORG, '/login/sessionCookieRedirect?token=', session.cookieToken,
                        '&redirectUrl=', redirect])

    usersResourceClient = UsersResourceClient(OKTA_ORG, API_TOKEN)
    user = usersResourceClient.get_user(uid=session.userId)

    # Setup THIS app's session now that we've posted the Okta session
    s = UserSession(id=session.id, userId=session.userId,
                    login=user.profile.login,
                    firstName=user.profile.firstName,
                    lastName=user.profile.lastName
                    )
    serializer = SessionSerializer(s)
    request.session['session'] = JSONRenderer().render(serializer.data)

    return HttpResponseRedirect(postback)


def SecondFAView(request):
    c = None
    if 'session' in request.session:
        session = _getSession(request.session['session'])
        c = {'dict': {'session': session}}

    return render(request, 'registration/second-fa.html', c)


def dashboard(request):
    if 'session' in request.session:
        json = request.session['session']
        session = Utils.deserialize(json, UserSession)
        print('This session belongs to {0} {1} {2}'.format(session.firstName, session.lastName, session.userId))

        c = {'dict': {'session': session}}
        return render(request, 'dashboard.html', c)

    return render(request, 'dashboard.html')


def logout(request):
    if 'session' in request.session:
        try:
            sessionCli = SessionsClient(OKTA_ORG, API_TOKEN)
            sessionCli.clear_session(session.id)
        except Exception as e:
            print('some error: {}'.format(e))

        del request.session['session']

    return render(request, 'logged_out.html')


def RegistrationView(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            fn = form.cleaned_data['firstName']
            ln = form.cleaned_data['lastName']
            email = form.cleaned_data['email']
            pw = form.cleaned_data['password1']

            try:
                # Create a user client
                usersClient = UsersClient(OKTA_ORG, API_TOKEN)

                # Create credentials object to hold the password for this user
                password = Password()
                password.value = pw
                creds = LoginCredentials()
                creds.password = password

                # user to create. Load the password/credentials also
                u = User(login=email,
                         email=email,
                         firstName=fn,
                         lastName=ln
                         )
                u.credentials = creds

                # Post the user to the create user API
                result = usersClient.create_user(u, activate=True)
                # Check the return to see if the user has been created
                profile = result.profile
                # If successfully created, return to the success message page
                if profile.login == email:
                    return HttpResponseRedirect(reverse('registration_success'))

            except Exception as e:
                print("Error: {}".format(e))
                form.add_error(field=None, error=e)

    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def registration_success(request):
    return render(request, 'registration/success.html')


def _getSession(json):
    if json is not None:
        serializer = SessionSerializer(data=JSONParser().parse(BytesIO(json)))
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    return None


def verify(request, p=None):
    c = None

    if request.method == 'POST':
        form = mfaForm(request.POST)
        if 'session' in request.session:
            session = _getSession(request.session['session'])
            c = {'dict': {'session': session, 'form': form}}

        print("code = {0}, factor: {1}, token: {2}".format(request.POST['code'], request.POST['factorId'],
                                                           request.POST['stateToken']))
        authCli = AuthClient2(OKTA_ORG, API_TOKEN)

        try:
            pass_code = None
            if 'verify_code' in request.POST:
                pass_code = request.POST['code']

            auth = authCli.auth_with_factor(state_token=request.POST['stateToken'],
                                            factor_id=request.POST['factorId'],
                                            passcode=pass_code)

            if auth.status == 'SUCCESS':
                return _setCookieTokenAndLoadDash(request, auth.sessionToken)

        except Exception as err:
            form.add_error(field=None, error=err)

    return render(request, 'registration/second-fa.html', c)


