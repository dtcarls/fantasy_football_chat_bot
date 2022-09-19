import unittest


import requests_mock


from ff_bot.ff_bot import (SlackBot, SlackException, )


class SlackTestCase(unittest.TestCase):
    '''Test SlackBot class'''

    def setUp(self):
        self.url = "https://hooks.slack.com/services/A1B2C3/ABC1ABC2/abcABC1abcABC2"
        self.test_bot = SlackBot(self.url)
        self.test_text = "This is a test."

    @requests_mock.Mocker()
    def test_send_message(self, m):
        '''Does the message send successfully?'''
        m.post(self.url, status_code=200)
        self.assertEqual(self.test_bot.send_message(self.test_text).status_code, 200)

    @requests_mock.Mocker()
    def test_bad_bot_id(self, m):
        '''Does the expected error raise when a bot id is incorrect?'''
        m.post(self.url, status_code=404)
        with self.assertRaises(SlackException):
            self.test_bot.send_message(self.test_text)
