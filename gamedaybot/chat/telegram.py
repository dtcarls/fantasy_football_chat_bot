import requests
import json
import logging

logger = logging.getLogger(__name__)


class TelegramException(Exception):
    pass


class Telegram(object):
    """
    A class used to send messages to a Telegram chat through the Bot API.

    Parameters
    ----------
    token : str
        The token of the Telegram bot.
    chat_id : str
        The ID of the Telegram chat to send messages to.

    Attributes
    ----------
    token : str
        The token of the Telegram bot.
    chat_id : str
        The ID of the Telegram chat to send messages to.

    Methods
    -------
    send_message(text: str)
        Sends a message to the Telegram chat.
    """

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def __repr__(self):
        return f"Telegram(token={self.token}, chat_id={self.chat_id})"

    def send_message(self, text):
        """
        Sends a message to the Telegram chat.

        Parameters
        ----------
        text : str
            The message to be sent to the Telegram chat.

        Returns
        -------
        r : requests.Response
            The response object of the POST request.

        Raises
        ------
        TelegramException
            If there is an error with the POST request.
        """

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': text
        }

        headers = {'content-type': 'application/json'}

        r = requests.post(url, json=payload, headers=headers)

        if r.status_code != 200:
            print(r.json())
            logger.error(r.content)
            raise TelegramException(r.content)

        return r
