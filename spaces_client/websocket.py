"""Websocket connection to Avaya Spaces"""


from asyncio import Future
import logging

import socketio


web_socket_URL = "https://spacesapis-socket.avayacloud.com/chat"

class SpacesWebSocket:
    """Wrapper for the Socket.IO websocket connection to Spaces.

    listener is the callback used for reporting received chat messages, via the
    on_chat_message(body_text, sender, space) method."""

    def __init__(self, auth_query, listener):
        self.auth_query = auth_query
        self.listener = listener
        self.sio = socketio.AsyncClient()
        self.bind_events()
        self.connect_future = None

    def bind_events(self):
        self.sio.on('connect', self.on_connect)
        self.sio.on('connect_error', self.on_connect_error)
        self.sio.on('disconnect', self.on_disconnect)
        # /chat namespace is the one actually used by Spaces
        self.sio.on('connect', self.on_chat_connect, namespace='/chat')
        self.sio.on('connect_error', self.on_chat_connect_error, namespace='/chat')
        self.sio.on('CHANNEL_SUBSCRIBED', self.on_channel_subscribed, namespace='/chat')
        self.sio.on('MESSAGE_SENT', self.on_message_sent, namespace='/chat')

    async def connect(self):
        assert self.auth_query != None
        assert self.connect_future == None

        url = '{}?{}'.format(web_socket_URL, self.auth_query)
        self.connect_future = Future()
        await self.sio.connect(url, transports='websocket', namespaces=['/chat'])
        await self.connect_future

    async def disconnect(self):
        self.connect_future = None
        await self.sio.disconnect()

    def on_connect(self):
        logging.info("Socket connected")

    def on_connect_error(self, error):
        logging.warning("Socket connection failed: %s", error)

    def on_disconnect(self):
        logging.info("Socket disconnected")

    def on_chat_connect(self):
        logging.info("/chat Socket connected")
        self.connect_future.set_result(True)

    def on_chat_connect_error(self, error):
        logging.warning("/chat Socket connection failed: %s", error)
        self.connect_future.set_exception(error)

    def on_channel_subscribed(self, message):
        logging.info("Received channel subscribed: %s", str(message))

    def on_message_sent(self, message):
        logging.info("Received message: %s", str(message))
        if message['category'] == 'chat':
            body_text = message['content']['bodyText']
            space = {
                '_id': message['topicId'],
                'title': message['topicTitle'],
                'type': message['topicType']
            }
            self.listener(body_text,  message['sender'], space)

    async def send_subscribe_space(self, space_id, password=None):
        channel = make_channel_dict(space_id)
        if (password != None):
            channel['password'] = password
        payload = {
            'channel': channel
        }
        await self.sio.emit("SUBSCRIBE_CHANNEL", payload, namespace='/chat')

    async def send_unsubscribe_space(self, space_id):
        payload = {
            'channel': make_channel_dict(space_id)
        }
        await self.sio.emit("UNSUBSCRIBE_CHANNEL", payload, namespace='/chat')

    async def send_chat_message(self, message, space_id, sender_id):
        payload = {
            'content': {
                    'bodyText': message,
                    'data': []
            },
            'sender': {
                    '_id': sender_id,
                    'type': 'user'
            },
            'topicId': space_id,
            'category': 'chat'
        }
        await self.sio.emit("SEND_MESSAGE", payload, namespace='/chat')

def make_channel_dict(space_id):
    return {
        '_id': space_id,
        'type': 'topic'
    }
