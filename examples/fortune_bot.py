#!/usr/bin/env python3
"""Sample use of Avaya Spaces chat as a registered user.

This logs in to a space and monitors the messages in that space. If it sees a
message starting with "@fortune", it sends a chat message with a random string
from the Unix fortune(1) program."""


from argparse import ArgumentParser
from asyncio import run, create_task, get_event_loop, sleep
import re
from subprocess import check_output

from spaces_client import *


# ID of the space to enter if one isn't provided on the command line
default_space_id = "space ID goes here"

# Token used for authentication - see docs for details
refresh_token = "refresh token value goes here"

# Client ID and secret needed for OAuth2 - see docs for details
client_id = None
client_secret = None

def read_client_data():
    "Read the client ID and secret from a file in the current directory."
    global client_id
    global client_secret
    with open(".client_data") as f:
        for line in f:
            if '=' in line:
                key, value = line.split('=')
                key = key.strip()
                if key == 'client_id':
                    client_id = value.strip()
                elif key == 'client_secret':
                    client_secret = value.strip()

fortune_command = ("fortune", "-s", "fortunes")

def fortune():
    "Returns a random string from fortune(1)."
    return check_output(fortune_command, universal_newlines=True)[:-1]

# Based on <https://medium.com/@jorlugaqui/how-to-strip-html-tags-from-a-string-in-python-7cb81a2bbf44>
html_tag_re = re.compile('<.*?>')
def remove_html_tags(text):
    """Remove html tags from a string"""
    return re.sub(html_tag_re, '', text)

class FortuneBot:

    def __init__(self, space_id):
        self.space_id = space_id

        self.auth = Oauth2Authenticator(client_id, client_secret)
        self.auth.refresh_token = refresh_token
        self.auth.refresh_access_token()

        self.user = RegisteredUser(self.auth)

    async def main(self):
        self.user.login()

        self.chat = SpacesSession(self.user)
        self.chat.add_chat_listener(self.on_chat_message)
        await self.chat.start()

        await self.chat.enter_group_space(self.space_id)

    def on_chat_message(self, body_text, sender, space):
        plain_text = remove_html_tags(body_text).strip()
        if plain_text.startswith('@fortune'):
            create_task(self.send_fortune())

    async def send_fortune(self):
        await self.chat.send_group_chat_message(fortune())

def main(space_id):
    fortunebot = FortuneBot(space_id)
    loop = get_event_loop()
    try:
        loop.run_until_complete(fortunebot.main())
        loop.run_forever()
    finally:
        loop.close()

if __name__ == '__main__':
    parser = ArgumentParser(description="Launch a fortune bot in a Space")
    parser.add_argument('space_id', nargs='?', default=default_space_id)
    args = parser.parse_args()

    read_client_data()
    main(args.space_id)
