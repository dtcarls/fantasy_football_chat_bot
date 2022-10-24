import requests
import json
import logging

logger = logging.getLogger(__name__)

class SlackException(Exception):
    pass

class Slack(object):
    # Creates GroupMe Bot to send messages
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def __repr__(self):
        return "Slack Webhook Url(%s)" % self.webhook_url

    def send_message(self, text):
        # Sends a message to the chatroom
        message = "```{0}```".format(text)
        template = {
            "text": message #limit 40000
        }

        headers = {'content-type': 'application/json'}

        if self.webhook_url not in (1, "1", ''):
            r = requests.post(self.webhook_url,
                              data=json.dumps(template), headers=headers)

            if r.status_code != 200:
                logger.error(r.content)
                raise SlackException(r.content)

            return r