import requests
import json
import logging

logger = logging.getLogger(__name__)

class GroupMeException(Exception):
    pass

class GroupMe(object):
    # Creates GroupMe Bot to send messages
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def __repr__(self):
        return "GroupMeBot(%s)" % self.bot_id

    def send_message(self, text):
        # Sends a message to the chatroom
        template = {
            "bot_id": self.bot_id,
            "text": text, #limit 1000 chars
            "attachments": []
        }

        headers = {'content-type': 'application/json'}

        if self.bot_id not in (1, "1", ''):
            r = requests.post("https://api.groupme.com/v3/bots/post",
                              data=json.dumps(template), headers=headers)
            if r.status_code != 202:
                logger.error(r.content)
                raise GroupMeException(r.content)

            return r
