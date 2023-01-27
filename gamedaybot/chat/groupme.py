import requests
import json
import logging

logger = logging.getLogger(__name__)


class GroupMeException(Exception):
    pass


class GroupMe(object):
    """
    Creates a GroupMe bot to send messages to a specified chatroom.

    Parameters:
    bot_id (str): The unique bot ID for the GroupMe chatroom.

    Attributes:
    bot_id (str): The unique bot ID for the GroupMe chatroom.
    """

    def __init__(self, bot_id):
        self.bot_id = bot_id

    def __repr__(self):
        return "GroupMeBot(%s)" % self.bot_id

    def send_message(self, text):
        """
        Sends a message to the specified GroupMe chatroom.

        Parameters:
        text (str): The message to be sent to the chatroom. Limit 1000 characters.

        Returns:
        r (requests.Response): The response from the GroupMe API.
        """
        template = {
            "bot_id": self.bot_id,
            "text": text,
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
