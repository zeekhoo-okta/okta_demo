from okta.UsersClient import UsersClient
from okta.framework.Utils import Utils
from models.app.AppLinks import AppLinks


class UsersResourceClient(UsersClient):
    def __init__(self, base_url, api_token):
        UsersClient.__init__(self, base_url, api_token)

    def get_app_links(self, uid):
        response = UsersClient.get_path(self, '/{}/appLinks'.format(uid))
        return Utils.deserialize(response.text, AppLinks)

    def query_user(self, login):
        response = UsersClient.get_path(self, '?q={}'.format(login))
        return Utils.deserialize(response.text, AppLinks)
