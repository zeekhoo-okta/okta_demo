import json

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils.six import BytesIO
from django.http import HttpResponseRedirect, HttpResponse

from okta import AuthClient, SessionsClient, UsersClient
from okta.framework.ApiClient import ApiClient
from okta.framework.Utils import Utils
from okta.models.session.Session import Session
from okta.models.user import User, UserProfile
from okta.models.user.LoginCredentials import LoginCredentials, Password, RecoveryQuestion
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from api.AuthClient2 import AuthClient2
from api.RestClient import RestClient
from api.UsersResourceClient import UsersResourceClient
from okta_proj.api.models.session.UserSession import UserSession
from serializers.SessionSerializer import SessionSerializer
from .forms import LoginForm, RegistrationForm, mfaForm, ActivationForm

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

            redirect = None
            form_value = form.cleaned_data['redirect']
            if form_value.startswith('http'):
                redirect = form_value

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
                    return _setCookieTokenAndLoadDash(request=request, session_token=auth.sessionToken, redirectUri=redirect)

            except Exception as oktaError:
                form.add_error(field=None, error=oktaError)
        else:
            print('Form is not valid')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    c = {'dict': {'session': session, 'form': form}}
    return render(request, 'registration/login.html', c)


def session(request):
    if request.method == 'POST':
        session = json.loads(request.body)
        print('session = {}'.format(session))
        user_id = session['userId']
        print('session = {}'.format(session['id']))

        usersResourceClient = UsersResourceClient(OKTA_ORG, API_TOKEN)
        user = usersResourceClient.get_user(uid=user_id)
        s = UserSession(id=session['id'], userId=session['userId'],
                        login=user.profile.login,
                        firstName=user.profile.firstName,
                        lastName=user.profile.lastName
                        )
        serializer = SessionSerializer(s)
        request.session['session'] = JSONRenderer().render(serializer.data)
        request.session['id'] = session['id']

        response = HttpResponse()
        response.status_code = 200
        return response

    return HttpResponseRedirect(reverse('home'))



def _setCookieTokenAndLoadDash(request, session_token, redirectUri=None):
    sessionCli = SessionsClient(OKTA_ORG, API_TOKEN)
    session = sessionCli.create_session_by_session_token(session_token=session_token, additional_fields='cookieToken')

    if redirectUri is not None and redirectUri.startswith('http'):
        print('redirect uri = {}'.format(redirectUri))
        redirect = redirectUri
    else:
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


def intranet(request):
    return render(request, 'intranet.html')


def logout(request):
    if 'session' in request.session:
        try:
            json = request.session['session']
            session = Utils.deserialize(json, UserSession)

            #sessionCli = SessionsClient(OKTA_ORG, API_TOKEN)
            #print('logging out session {}'.format(session.id))
            #sessionCli.clear_session(session.id)
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
                         email='zee.khoo@okta.com',
                         firstName=fn,
                         lastName=ln
                         )
                u.credentials = creds

                # Post the user to the create user API
                result = usersClient.create_user(u, activate=False)

                # Check the return to see if the user has been created
                profile = result.profile
                # If successfully created, return to the success message page
                if profile.login == email:
                    user_id = result.id
                    print('created user {}'.format(user_id))

                    rc = RestClient(OKTA_ORG, API_TOKEN)

                    # Create user in default group
                    groupadded = rc.group_add('00gxb3pl2cWg2mFGP1t6', user_id)

                    redirect = form.cleaned_data['redirect']
                    lang = form.cleaned_data['lang']
                    profile_data = {
                        "id": user_id,
                        "profile": {
                            "registration_redirect_url": redirect,
                            "lang": lang
                        }
                    }
                    rc.users_post(user_id=user_id, post_data=profile_data)

                    return HttpResponseRedirect(reverse('registration_success'))

            except Exception as e:
                print("Error: {}".format(e))
                form.add_error(field=None, error=e)

    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def registration_success(request):
    return render(request, 'registration/success.html')


def ActivationView(request, userid):
    print('activating user {}'.format(userid))

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ActivationForm(request.POST)

        if form.is_valid():
            pw = form.cleaned_data['password']

            try:
                rc = RestClient(OKTA_ORG, API_TOKEN)
                activated = rc.user_activate(userid)

                # If authentication is successful, exchange the session token for a session cookie
                if activated == 200:
                    user = rc.users_get(userid)
                    profile = user['profile']
                    login = profile['login']
                    redirect = profile['registration_redirect_url']

                    authCli = AuthClient2(OKTA_ORG, API_TOKEN)
                    auth = authCli.authenticate(username=login, password=pw)
                    status = auth.status
                    print('login status = {}'.format(status))
                    if status == 'SUCCESS':
                        return _setCookieTokenAndLoadDash(request=request, session_token=auth.sessionToken,
                                                          redirectUri=redirect)


            except Exception as oktaError:
                form.add_error(field=None, error=oktaError)
        else:
            print('Form is not valid')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ActivationForm()

    c = {'form': form, 'userid': userid}
    return render(request, 'registration/activate.html', c)


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


