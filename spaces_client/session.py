"""A session for being connected to Avaya Spaces."""


import requests

from .websocket import SpacesWebSocket


class SpacesSession:
    "An authenticated session with Avaya Spaces."

    def __init__(self, user):
        self.user = user
        self.websocket = None
        self.group_space_id = None
        self.chat_listeners = []

    def add_chat_listener(self, listener):
        """Register a listener to handle incoming chat messages.

        The listener must be a callable that accepts three arguments
        (body_text, sender, space).
        body_text - the HTML text of the message
        sender - a dictionary containing data about the sender
        space - a dictionary containing data about the space the message is in"""
        self.chat_listeners.append(listener)

    def remove_chat_listener(self, listener):
        "Remove a listener for incoming chat messages."
        self.chat_listeners.remove(listener)

    async def start(self):
        assert self.websocket == None
        assert self.user.auth.has_token()

        auth_query = self.user.auth.get_websocket_auth_query()
        self.websocket = SpacesWebSocket(auth_query, self.on_chat_message)
        await self.websocket.connect()

    async def stop(self):
        assert self.websocket != None

        await self.websocket.disconnect()
        self.websocket = None

    async def enter_group_space(self, space_id):
        # TODO: validate the space ID
        if self.group_space_id != None:
            self.leave_group_space()

        await self.websocket.send_subscribe_space(space_id)
        self.group_space_id = space_id

    async def leave_group_space(self):
        assert self.group_space_id != None

        await self.websocket.send_unsubscribe_space(self.group_space_id)
        self.group_space_id = None

    async def send_group_chat_message(self, text):
        "Send a chat message to the current group space."
        assert self.group_space_id != None

        await self.websocket.send_chat_message(text, self.group_space_id,
                                                   self.user.id)

    def on_chat_message(self, body_text, sender, space):
        for listener in self.chat_listeners:
            listener(body_text, sender, space)

    def get_space_info(self, space_id):
        url = 'https://spacesapis.avayacloud.com/api/spaces/{}'.format(space_id)
        headers = {'Authorization': self.user.auth.get_authorization_value()}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()
