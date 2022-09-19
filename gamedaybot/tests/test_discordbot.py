import unittest


import requests_mock


from ff_bot.ff_bot import (DiscordBot, DiscordException, )


class DiscordTestCase(unittest.TestCase):
    '''Test DiscordBot class'''

    def setUp(self):
        self.url = "https://discordapp.com/api/webhooks/123/abc"
        self.test_bot = DiscordBot(self.url)
        self.test_text = "This is a test."

    @requests_mock.Mocker()
    def test_send_message(self, m):
        '''Does the message send successfully?'''
        m.post(self.url, status_code=204)
        self.assertEqual(self.test_bot.send_message(self.test_text).status_code, 204)

    @requests_mock.Mocker()
    def test_bad_bot_id(self, m):
        '''Does the expected error raise when a bot id is incorrect?'''
        m.post(self.url, status_code=404)
        with self.assertRaises(DiscordException):
            self.test_bot.send_message(self.test_text)
