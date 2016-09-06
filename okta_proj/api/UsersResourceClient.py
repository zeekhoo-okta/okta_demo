from okta.UsersClient import UsersClient
from okta.framework.Utils import Utils
from okta.models.user.User import User

from okta_proj.api.models.user.AppLinks import AppLinks


class UsersResourceClient(UsersClient):
    def __init__(self, base_url, api_token):
        UsersClient.__init__(self, base_url, api_token)

    def get_user(self, uid):
        response = UsersClient.get_path(self, '/{}'.format(uid))
        return Utils.deserialize(response.text, User)

    def get_app_links(self, uid):
        response = UsersClient.get_path(self, '/{}/appLinks'.format(uid))
        return Utils.deserialize(response.text, AppLinks)

    def query_user(self, login):
        response = UsersClient.get_path(self, '?q={}'.format(login))
        return Utils.deserialize(response.text, AppLinks)
