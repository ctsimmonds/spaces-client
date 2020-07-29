#!/usr/bin/env python3
"""Sample use of Avaya Spaces chat as an anonymous guest user.

This logs in as a new anonymous guest user, enters a certain public space,
sends a chat message in that space as well as printing any messages received
in the space for a minute."""


from argparse import ArgumentParser
from asyncio import run, sleep

from spaces_client import *


# ID of the space to enter if one isn't provided on the command line
default_space_id = "space ID goes here"

# Display name for the anonymous guest user
display_name = "Mr. Anonymous"

# Text of message to send in the space
message_text = "Hello from guest_chat.py"

def on_chat_message(user, body_text, sender, space):
    if sender['_id'] == user.id:
        # Message from self - ignore
        return
    print('Received message "{}" from "{}" in space "{}"'.format(
        body_text, sender['displayname'], space['title']))

async def main(space_id):
    user = AnonymousUser(display_name)

    print('Logging in as guest user "{}"'.format(display_name))
    user.login()

    chat = SpacesSession(user)
    chat.add_chat_listener(lambda a, b, c: on_chat_message(user, a, b, c))
    await chat.start()

    space = chat.get_space_info(space_id)
    space_name = space['title']

    await sleep(1)
    print('Entering space "{}"'.format(space_name))
    await chat.enter_group_space(space_id)

    await sleep(1)
    print("Sending a text message to the space")
    await chat.send_group_chat_message(message_text)

    print("Waiting one minute for any other messages in the space")
    await sleep(60)

    await chat.leave_group_space()
    await chat.stop()

if __name__ == '__main__':
    parser = ArgumentParser(description="Briefly join a Space as a guest chat participant")
    parser.add_argument('space_id', nargs='?', default=default_space_id)
    args = parser.parse_args()

    run(main(args.space_id))
