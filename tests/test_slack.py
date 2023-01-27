import pytest
import sys
import os
sys.path.insert(1, os.path.abspath('.'))
from gamedaybot.chat.slack import (Slack, SlackException, )


@pytest.mark.usefixtures("mock_requests")
class TestSlack:
    '''Test SlackBot class'''

    def setup_method(self):
        self.url = "https://hooks.slack.com/services/A1B2C3/ABC1ABC2/abcABC1abcABC2"
        self.test_bot = Slack(self.url)
        self.test_text = "This is a test."

    def test_send_message(self, mock_requests):
        '''Does the message send successfully?'''
        mock_requests.post(self.url, status_code=200)
        assert self.test_bot.send_message(self.test_text).status_code == 200

    def test_bad_bot_id(self, mock_requests):
        '''Does the expected error raise when a bot id is incorrect?'''
        mock_requests.post(self.url, status_code=404)
        with pytest.raises(SlackException):
            self.test_bot.send_message(self.test_text)
