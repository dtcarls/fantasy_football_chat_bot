import unittest


import requests_mock


from ff_bot.ff_bot import (GroupMeBot, GroupMeException, )


class GroupMeBotTestCase(unittest.TestCase):
    '''Test GroupMeBot class'''

    def setUp(self):
        self.test_bot = GroupMeBot("123456")
        self.test_text = "This is a test."

    @requests_mock.Mocker()
    def test_send_message(self, m):
        '''Does the message send successfully?'''
        m.post("https://api.groupme.com/v3/bots/post", status_code=202)
        self.assertEqual(self.test_bot.send_message(self.test_text).status_code, 202)

    @requests_mock.Mocker()
    def test_bad_bot_id(self, m):
        '''Does the expected error raise when a bot id is incorrect?'''
        m.post("https://api.groupme.com/v3/bots/post", status_code=404)
        with self.assertRaises(GroupMeException):
            self.test_bot.send_message(self.test_text)
