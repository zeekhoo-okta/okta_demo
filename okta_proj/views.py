from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import LoginForm
from okta import UsersClient, AuthClient, SessionsClient, AppInstanceClient
from okta.models.user import User


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

                redirect = None
                if cookie:
                    apps = None
                    try:
                        appCli = AppInstanceClient(org, token)
                        apps = appCli.get_app_instances()
                    except Exception as oktaError:
                        form.add_error(field=None, error=oktaError)

                    for app in apps:
                        print("Apps: {}".format(app.name))
                        if app.name == settings.OKTA_SFDC_APP_NAME:
                            if app._links:
                                if app._links.appLinks:
                                    for link in app._links.appLinks:
                                        print("Link = {0} : {1}".format(link.name, link.href))
                                        if link.name == 'mc':
                                            redirect = link.href

                    if redirect:
                        redirect = ''.join([org, '/login/sessionCookieRedirect?token=', cookie, '&redirectUrl=', redirect])
                        return HttpResponseRedirect(redirect)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})