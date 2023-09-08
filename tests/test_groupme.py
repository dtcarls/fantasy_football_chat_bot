import pytest
import sys
import os
sys.path.insert(1, os.path.abspath('.'))
from gamedaybot.chat.groupme import (GroupMe, GroupMeException, )


@pytest.mark.usefixtures("mock_requests")
class TestGroupMeBot:
    '''Test GroupMeBot class'''

    def setup_method(self):
        self.test_bot = GroupMe("123456")
        self.test_text = "This is a test."

    def test_send_message(self, mock_requests):
        '''Does the message send successfully?'''
        mock_requests.post("https://api.groupme.com/v3/bots/post", status_code=202)
        assert self.test_bot.send_message(self.test_text).status_code == 202

    def test_bad_bot_id(self, mock_requests):
        '''Does the expected error raise when a bot id is incorrect?'''
        mock_requests.post("https://api.groupme.com/v3/bots/post", status_code=404)
        with pytest.raises(GroupMeException):
            self.test_bot.send_message(self.test_text)
