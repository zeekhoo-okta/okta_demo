from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from okta import AuthClient, SessionsClient
from api.AppInstanceClient import AppInstanceClient
from .forms import LoginForm


def LoginView(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            redirect = reverse_lazy('home')

            un = form.cleaned_data['username']
            pw = form.cleaned_data['password']
            org = ''.join(['https://', settings.OKTA_ORG])
            token = settings.OKTA_API_TOKEN
            if org and token:
                #usersClient = UsersClient(''.join(['https://', settings.OKTA_ORG]), settings.OKTA_API_TOKEN)
                #zee = User(login='robot.zee1@email.com',
                #           email='zee.robot@zeekhoo.com',
                #           firstName='Zman',
                #           lastName='Kman')
                #u = usersClient.create_user(zee, activate=False)

                status = 'FAIL'
                try:
                    authCli = AuthClient(org, token)
                    auth = authCli.authenticate(username=un, password=pw)
                    status = auth.status
                    print('status = {}'.format(status))
                except Exception as oktaError:
                    form.add_error(field=None, error=oktaError)

                cookie = None
                if status == 'SUCCESS':
                    session_token = auth.sessionToken
                    try:
                        sessionCli = SessionsClient(org, token)
                        session = sessionCli.create_session_by_session_token(session_token=session_token,
                                                                             additional_fields='cookieToken')
                        cookie = session.cookieToken
                    except Exception as oktaError:
                        form.add_error(field=None, error=oktaError)

                if cookie:
                    try:
                        appCli = AppInstanceClient(org, token)
                        apps = appCli.get_app_instances()
                        for app in apps:
                            print("Apps: {}".format(app.name))
                            if app.name == settings.OKTA_SFDC_APP_NAME:
                                if app._links:
                                    if app._links.appLinks:
                                        for link in app._links.appLinks:
                                            if link.name == 'mc':
                                                redirect = ''.join([org,
                                                                    '/login/sessionCookieRedirect?token=', cookie,
                                                                    '&redirectUrl=', link.href])
                                                return HttpResponseRedirect(redirect)
                    except Exception as oktaError:
                        form.add_error(field=None, error=oktaError)

            #return HttpResponseRedirect(redirect)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})