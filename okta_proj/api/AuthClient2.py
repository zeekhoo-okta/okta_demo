from okta.AuthClient import AuthClient
from okta.framework.ApiClient import ApiClient
from okta.framework.Utils import Utils

from okta_proj.api.models.auth.AuthResult2 import AuthResult2


class AuthClient2(AuthClient):
    def __init__(self, base_url, api_token):
        AuthClient.__init__(self, base_url=base_url, api_token=api_token)

    def authenticate(self, username, password,
                     relay_state=None, response_type=None, force_mfa=None, context=None):

        request = {
            'username': username,
            'password': password,
            'relayState': relay_state,
            'context': context
        }

        params = {
            'force_mfa': force_mfa,
            'response_type': response_type
        }

        response = ApiClient.post_path(self, '/', request, params=params)
        return Utils.deserialize(response.text, AuthResult2)


    def auth_with_factor(self, state_token, factor_id, passcode=None,
                         relay_state=None, remember_device=None):
        request = {
            'stateToken': state_token,
            'passCode': passcode,
            'relayState': relay_state
        }

        params = {
            'rememberDevice': remember_device
        }

        response = ApiClient.post_path(self, '/factors/{0}/verify'.format(factor_id),
                                       request, params=params)
        return Utils.deserialize(response.text, AuthResult2)