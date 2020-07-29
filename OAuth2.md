Use of OAuth2 with Spaces
=========================

For info on the use of OAuth2 with Spaces, see the developer documentation:
* [Authorizing Requests](https://spaces.zang.io/developers/docs/tutorials/authorizingrequests)
* [Registering an Application](https://spaces.zang.io/developers/docs/guides/register)

To briefly summarize, you will need a client ID and a client secret to make use
of OAuth2, obtainable through the registration program. Sample programs using
OAuth2 will read them from a text file in the same directory with the following
simple format:

    client_id = your-client-id-here
    client_secret = your-client-secret-here

There are OAuth2 libraries available for Python, but I found it easiest to just
login in to the desired account from another client and extract the refresh
token from that and use it.
