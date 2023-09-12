import pytest
import sys
import os
sys.path.insert(1, os.path.abspath('.'))
from gamedaybot.chat.discord import (Discord, DiscordException, )


@pytest.mark.usefixtures("mock_requests")
class TestDiscord:
    '''Test DiscordBot class'''

    def setup_method(self):
        self.url = "https://discordapp.com/api/webhooks/123/abc"
        self.test_bot = Discord(self.url)
        self.test_text = "This is a test."

    def test_send_message(self, mock_requests):
        '''Does the message send successfully?'''
        mock_requests.post(self.url, status_code=204)
        assert self.test_bot.send_message(self.test_text).status_code == 204

    def test_bad_bot_id(self, mock_requests):
        '''Does the expected error raise when a bot id is incorrect?'''
        mock_requests.post(self.url, status_code=404)
        with pytest.raises(DiscordException):
            self.test_bot.send_message(self.test_text)
