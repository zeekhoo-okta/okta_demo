from okta.models.user.User import User

from okta_proj.api.models.factor.Factor2 import Factor2


class Embedded2:

    types = {
        'user': User,
        'factors': Factor2
    }

    def __init__(self):

        self.user = None

        self.factors = None