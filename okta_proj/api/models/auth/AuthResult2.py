from okta_proj.api.models.Embedded2 import Embedded2


class AuthResult2:

    types = {
        'stateToken': str,
        'status': str,
        'expiresAt': str,
        'relayState': str,
        'factorResult': str,
        'factorResultMessage': str,
        'recoveryToken': str,
        'sessionToken': str,
        'idToken': str,
        '_embedded': Embedded2
    }

    alt_names = {
        '_embedded': 'embedded'
    }

    def __init__(self):

        self.stateToken = None  # str

        self.status = None  # str

        self.expiresAt = None  # str

        self.relayState = None  # str

        self.factorResult = None  # str

        self.factorResultMessage = None  # str

        self.recoveryToken = None  # str

        self.sessionToken = None  # str

        self.idToken = None  # str

        self.embedded = None # Embedded