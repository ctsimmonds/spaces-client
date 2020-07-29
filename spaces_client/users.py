"""Support for authenticating with Avaya Spaces as a user."""


import requests


class AbstractUser:

    def __init__(self, auth):
        self.id = None
        self.auth = auth

    def fetch_user_data(self):
        url = 'https://spacesapis.avayacloud.com/api/users/me'
        headers = {'Authorization': self.auth.get_authorization_value()}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        self.user_info = r.json()
        self.id = self.user_info['_id']

class AnonymousUser(AbstractUser):
    """An anonymous guest user with limited temporary access to Avaya Spaces.

    Anonymous guest user auth tokens are only valid for 24 hours.

    See <https://spaces.zang.io/developers/docs/tutorials/authorizingrequests#section7>
    """

    def __init__(self, display_name):
        AbstractUser.__init__(self, AnonymousUserAuthenticator())
        self.display_name = display_name

    def login(self):
        self.auth.get_jwt(self.display_name)
        self.fetch_user_data()

class RegisteredUser(AbstractUser):
    """A registered user with an account on Avaya Spaces, using OAuth2 for
    authentication."""

    def __init__(self, auth):
        AbstractUser.__init__(self, auth)

    def login(self):
        self.fetch_user_data()

guest_auth_endpoint_URL = 'https://spacesapis.avayacloud.com/api/anonymous/auth'

class AbstractAuthenticator:
    "Abstract base class for managing a user's auth token."

    def __init__(self, token_type):
        self.access_token = None
        self.token_type = token_type

    def has_token(self):
        "Has the user successfully authenticated and got an auth token?"
        return self.access_token != None

    def get_websocket_auth_query(self):
        "Returns the query parameters needed to authenticate the websocket."
        assert self.has_token()

        return 'token={}&tokenType={}'.format(self.access_token, self.token_type)

class AnonymousUserAuthenticator(AbstractAuthenticator):
    "Manages the auth token for an anonymous guest user."

    def __init__(self):
        AbstractAuthenticator.__init__(self, 'jwt')

    def get_jwt(self, display_name):
        assert self.access_token is None

        payload = {
            'displayname': display_name,
            'username': '',
            'picturefile': ''
        }
        r = requests.post(guest_auth_endpoint_URL, data=payload)
        r.raise_for_status()
        self.access_token = r.json()['token']

    def get_authorization_value(self):
        "Return the value to use in the HTTP Authorization header."
        assert self.has_token()

        return 'jwt {}'.format(self.access_token)

# Spaces OAuth2 parameters
authorization_base_URL = "https://accounts.avayacloud.com/oauth2/authorize"
token_URL = "https://accounts.avayacloud.com/oauth2/access_token"

class Oauth2Authenticator(AbstractAuthenticator):
    "Manages the auth token for a registered user with OAuth2."

    def __init__(self, client_id, client_secret):
        AbstractAuthenticator.__init__(self, 'oauth')
        assert client_id != None
        assert client_secret != None
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = None

    def refresh_access_token(self):
        "Use the refresh token to get a new access token."
        assert self.refresh_token != None

        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        r = requests.post(token_URL, data=payload)
        r.raise_for_status()
        data = r.json()
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']

    def get_authorization_value(self):
        "Return the value to use in the HTTP Authorization header."
        assert self.has_token()

        return 'Bearer {}'.format(self.access_token)
