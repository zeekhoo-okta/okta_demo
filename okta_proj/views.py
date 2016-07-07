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
                usersClient = UsersClient(org, token)

                password = Password()
                password.value = pw
                creds = LoginCredentials()
                creds.password = password
                u = User(login=email,
                         email=email,
                         firstName=fn,
                         lastName=ln
                         )
                u.credentials = creds
                result = usersClient.create_user(u, activate=True)
                return HttpResponseRedirect('/register/success/')

            except Exception as e:
                print("Error: {}".format(e))
                form.add_error(field=None, error=e)

    else:
        form = RegistrationForm()

    variables = RequestContext(request, {'form': form})

    return render_to_response('registration/register.html', variables)


def LoginView(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)

        if form.is_valid():
            un = form.cleaned_data['username']
            pw = form.cleaned_data['password']
            print("logging in {0}".format(un))
            try:
                authCli = AuthClient(org, token)
                auth = authCli.authenticate(username=un, password=pw)
                status = auth.status
                print('status = {}'.format(status))
                if status == 'SUCCESS':
                    session_token = auth.sessionToken
                    sessionCli = SessionsClient(org, token)
                    session = sessionCli.create_session_by_session_token(session_token=session_token,
                                                                         additional_fields='cookieToken')
                    cookie = session.cookieToken
                    uid = session.userId

                    usersClient = UsersResourceClient(org, token)
                    appLinks = usersClient.get_app_links(uid=uid)

                    for appLink in appLinks:
                        print("app = {}".format(appLink.appName))
                        if appLink.appName == settings.OKTA_SFDC_APP_NAME:
                            redirect = ''.join([org,'/login/sessionCookieRedirect?token=', cookie,
                                                '&redirectUrl=', appLink.linkUrl])
                            return HttpResponseRedirect(redirect)

                    return HttpResponseRedirect('/login/message/')

            except Exception as oktaError:
                form.add_error(field=None, error=oktaError)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


def registration_success(request):
    return render_to_response('registration/success.html')


def message_no_saml(request):
    return render_to_response('message.html')
