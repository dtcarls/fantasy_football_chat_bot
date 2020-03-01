import requests
import json

class SlackException(Exception):
    pass

class SlackBot(object):
    #Creates GroupMe Bot to send messages
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def __repr__(self):
        return "Slack Webhook Url(%s)" % self.webhook_url

    def send_message(self, text):
        #Sends a message to the chatroom
        message = "```{0}```".format(text)
        template = {
                    "text":message
                    }

        headers = {'content-type': 'application/json'}

        if self.webhook_url not in (1, "1", ''):
            r = requests.post(self.webhook_url,
                              data=json.dumps(template), headers=headers)

            if r.status_code != 200:
                raise SlackException('WEBHOOK_URL')

            return r
