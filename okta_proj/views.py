from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect

from .forms import LoginForm
from django.shortcuts import render
from okta import UsersClient, AuthClient, SessionsClient, AppInstanceClient
from okta.models.user import User
from django.conf import settings


def LoginView(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            un = form.cleaned_data['username']
            pw = form.cleaned_data['password']
            org = ''.join(['https://', settings.OKTA_ORG])
            token = settings.OKTA_API_TOKEN
            if un and pw and org and token:
                print("username: {}".format(un))
                print("password: {}".format(pw))

                #usersClient = UsersClient(''.join(['https://', settings.OKTA_ORG]), settings.OKTA_API_TOKEN)
                #zee = User(login='robot.zee1@email.com',
                #           email='zee.robot@zeekhoo.com',
                #           firstName='Zman',
                #           lastName='Kman')
                #u = usersClient.create_user(zee, activate=False)

                status = ''
                try:
                    authCli = AuthClient(org, token)
                    auth = authCli.authenticate(username=un, password=pw)
                    status = auth.status
                    print('status = {}'.format(status))
                except Exception as e:
                    oktaError = e
                    print("error handling: {}".format(oktaError))
                    form.add_error(field=None, error=oktaError)

                cookie = ''
                if status == 'SUCCESS':
                    session_token = auth.sessionToken
                    print("session token = {}".format(session_token))
                    sessionCli = SessionsClient(org, token)
                    session = sessionCli.create_session_by_session_token(session_token=session_token,
                                                                         additional_fields='cookieToken')
                    cookie = session.cookieToken
                    print("cookie = {}".format(cookie))

                redirect = 'http://localhost:8000'
                if cookie:
                    appCli = AppInstanceClient(org, token)
                    apps = appCli.get_app_instances()
                    for app in apps:
                        print("Apps: {}".format(app.name))
                        if app.name == settings.OKTA_SFDC_APP_NAME:
                            x = '1'
                    redirect = ''.join([org, '/login/sessionCookieRedirect?token=', cookie, '&redirectUrl=', redirect])



                return HttpResponseRedirect(redirect)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})