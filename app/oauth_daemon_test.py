import os
import oauth_daemon
import unittest
import tempfile

class OauthTestCase(unittest.TestCase):

    def setUp(self):
        oauth_daemon.index()

if __name__ == '__main__':
    unittest.main()
