import requests
import json

class WhatsAppGroupException(Exception):
    pass

#https://developers.facebook.com/docs/whatsapp/api/messages/group
class WhatsAppGroupBot(object):
    #Creates WhatsAppGroup Bot to send messages
    def __init__(self, whatsapp_group_id):
        self.whatsapp_group_id = whatsapp_group_id

    def __repr__(self):
        return "WhatsAppGroupBot(%s)" % self.whatsapp_group_id

    def send_message(self, text):
        #Sends a message to the chatroom
        template = {
                    "recipient_type": "group",
                    "to": whatsapp_group_id,
                    "render_mentions": false,
                    "type": "text",
                    "text.body": text
                    }

        headers = {'content-type': 'application/json'}

        if self.whatsapp_group_id not in (1, "1", ''):
            r = requests.post("https://api.whatsapp.com/v1/messages",
                              data=json.dumps(template), headers=headers)
            if r.status_code != 202:
                raise WhatsAppGroupException('Invalid BOT_ID')

            return r