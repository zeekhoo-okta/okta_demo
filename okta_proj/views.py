from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from okta import AuthClient, SessionsClient, UsersClient
from api.UsersResourceClient import UsersResourceClient
from okta.models.user import User
from .forms import LoginForm, RegistrationForm
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from okta.models.user.LoginCredentials import LoginCredentials, Password

org = ''.join(['https://', settings.OKTA_ORG])
token = settings.OKTA_API_TOKEN


@csrf_protect
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
                usersClient = UsersClient(org, token)

                # Create credentials object to hold the password for this user
                password = Password()
                password.value = pw
                creds = LoginCredentials()
                creds.password = password

                # User to create. Load the password/credentials also
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
                    return HttpResponseRedirect('/register/success/')

            except Exception as e:
                print("Error: {}".format(e))
                form.add_error(field=None, error=e)

    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


@csrf_protect
def LoginView(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)

        if form.is_valid():
            un = form.cleaned_data['username']
            pw = form.cleaned_data['password']
            try:
                # Create an auth client and post the username and password
                authCli = AuthClient(org, token)
                auth = authCli.authenticate(username=un, password=pw)
                status = auth.status
                print('status = {}'.format(status))
                # If authentication is successful, exchange the session token for a session cookie
                if status == 'SUCCESS':
                    session_token = auth.sessionToken

                    # Create a session client
                    sessionCli = SessionsClient(org, token)
                    # Post the session token and get the session cookie token
                    session = sessionCli.create_session_by_session_token(session_token=session_token,
                                                                         additional_fields='cookieToken')
                    cookie = session.cookieToken

                    # We'll use the userId to get the user's app links
                    uid = session.userId
                    # Create a user client
                    usersClient = UsersResourceClient(org, token)
                    # Get the app links
                    appLinks = usersClient.get_app_links(uid=uid)

                    # Redirect to the message page if the Salesforce app is not assigned to this user
                    redirect = request.build_absolute_uri() + 'message'

                    for appLink in appLinks:
                        # Found the salesforce app in the app links. Get its redirect url and we'll redirect to it
                        if appLink.appName == settings.OKTA_SFDC_APP_NAME:
                            redirect = appLink.linkUrl

                    redirect = ''.join([org, '/login/sessionCookieRedirect?token=', cookie,
                                        '&redirectUrl=', redirect])
                    return HttpResponseRedirect(redirect)

            except Exception as oktaError:
                form.add_error(field=None, error=oktaError)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


def registration_success(request):
    return render(request, 'registration/success.html')


def message_no_saml(request):
    return render(request, 'message.html')
