from okta_proj.api.models.factor.Factor2 import Factor2


class UserSession:

    types = {
        'id': str,
        'userId': str,
        'login': str,
        'firstName': str,
        'lastName': str,
        'stateToken': str,
        'factors': Factor2,
    }

    def __init__(self, id=None, userId=None, login=None, firstName=None, lastName=None, stateToken=None, factors=None):
        self.id = id
        self.userId = userId
        self.login = login
        self.firstName = firstName
        self.lastName = lastName
        self.stateToken = stateToken
        self.factors = factors
