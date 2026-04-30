import unittest
from argparse import ArgumentParser
from configparser import ConfigParser

from crawler.frontier import *
from utils.config import Config


class MyTestCase(unittest.TestCase):
    def test_add_get_next_tbd_url(self):
        parser = ArgumentParser()
        parser.add_argument("--restart", action="store_true", default=False)
        parser.add_argument("--config_file", type=str, default="config.ini")
        args = parser.parse_args()
        config_file = args.config_file
        cparser = ConfigParser()
        cparser.read(config_file)
        config = Config(cparser)
        frontier = Frontier(config, True)
        starting_urls = {'https://www.ics.uci.edu','https://www.cs.uci.edu','https://www.informatics.uci.edu','https://www.stat.uci.edu'}
        my_urls = {'https://www.youtube.com', 'https://www.google.com', 'https://www.facebook.com'}

        for url in my_urls:
            frontier.add_url(url)

        self.assertEqual(True, frontier.get_tbd_url() in my_urls | starting_urls)
        self.assertEqual(True, frontier.get_tbd_url() in my_urls | starting_urls)
        self.assertEqual(True, frontier.get_tbd_url() in my_urls | starting_urls)
        self.assertEqual(True, frontier.get_tbd_url() in my_urls | starting_urls)
        self.assertEqual(True, frontier.get_tbd_url() in my_urls | starting_urls)
        self.assertEqual(True, frontier.get_tbd_url() in my_urls | starting_urls)
        self.assertEqual(True, frontier.get_tbd_url() in my_urls | starting_urls)



if __name__ == '__main__':
    unittest.main()
