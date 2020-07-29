spaces-client
=============

Python library for a chat client using Avaya Spaces.

.. _Avaya Spaces: https://spaces.avayacloud.com/

This provides a simple API and sample programs for participating in chats in
Spaces from Python.

Using the API
-------------

First, you'll need to create a user object. There are two possibilities -
anonymous guest users and registered users.

Anonymous guests have limited access and permissions in spaces and are only
valid for 24 hours, but are easy to use. Just create an instance of the
AnonymousUser class with a chosen display name and call login:

    user = AnonymousUser("John Doe")
    user.login()

Registered users require that an account has already been created at
https://accounts.avayacloud.com/ and need the use of OAuth2 for authentication
(see the accompanying document OAuth2.md for more details).

You'll need to first setup an instance of Oauth2Authenticator and then create
an instance of RegisteredUser and call login on it:

    auth = Oauth2Authenticator(client_id, client_secret)
    auth.refresh_token = refresh_token_value
    auth.refresh_access_token()
    user = RegisteredUser(auth)
    user.login()

After you have a user object, create an instance of SpacesSession with that user
and call start(). The API uses Python's asyncio, so any methods involving the
websocket are asynchronous and must be called using the await keyword:

    chat = SpacesSession(user)
    await chat.start()

To participate in a group space, call enter_group_space() and call
leave_group_space() to leave it. Sending a text message is done via the
send_group_chat_message() method:

    chat.enter_group_space(space_id)
    chat.send_group_chat_message("Hello, world!")
    chat.leave_group_space()

To receive messages from the joined group space, you need to register a callback
method with add_chat_listener(). The callback takes three parameters:
* body_text is the usually HTML formatted text of the message
* sender is a dictionary containing information about user that sent the message
* space is a dictionary containing details about that space

Example:

    def on_chat_message(body_text, sender, space):
        print('{} said {} in {}'.format(sender['title'], body_text, space['title']))
    chat.add_chat_listener(on_chat_message)
