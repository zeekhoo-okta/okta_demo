import requests
import json


class RestClient(object):
    def __init__(self, base_url, api_token):
        self.base_url = base_url + '/api/v1'
        self.api_token = api_token

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'SSWS ' + self.api_token
        }

    def users_get(self, user_id):
        response = requests.get(self.base_url + '/users/{}'.format(user_id), headers=self.headers)
        #print('me = {}'.format(response.json()))
        return response.json()

    def users_post(self, user_id, post_data):
        url = self.base_url + '/users/{}'.format(user_id)
        d = json.dumps(post_data)
        response = requests.post(url, headers=self.headers, data=d)

        return response.json()

    def user_activate(self, userid):
        response = requests.post(self.base_url + '/users/{}'.format(userid) + '/lifecycle/activate?sendEmail=false',
                                 headers=self.headers)
        print('activated user: {}'.format(response.status_code))
        print(response.json())
        return response.status_code

    def group_add(self, groupid, userid):
        response = requests.put(self.base_url + '/groups/{0}/users/{1}'.format(groupid, userid),
                                 headers=self.headers)
        print('group added user: {}'.format(response.status_code))
        return response.status_code
