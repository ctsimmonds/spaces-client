Example Programs
================

Included here are some sample programs demonstrating using of the Spaces Chat
API.

guest_chat.py
-------------

This demonstrates how to connect to a chat as an anonymous guest user.

It joins a particular space, sends a canned text message in that space, and then
waits for one minute before exitting. Any messages from other participants
during that minute are printed to the console.


fortune_bot.py
--------------

This is a sample participant in a Spaces chat as a registered user.

It runs as a bot in a particular space for dispensing wisdom via the Unix
fortune(1) command. Whenever any participant in the space sends a chat message
that begins with "@fortune", the bot emits a random saying to the space.
