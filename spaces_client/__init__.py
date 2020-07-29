from .users import AnonymousUser, RegisteredUser, Oauth2Authenticator
from .session import SpacesSession

__version__ = '0.1.0'

__all__ = ['__version__', 'AnonymousUser', 'RegisteredUser',
               'Oauth2Authenticator', 'SpacesSession' ]
