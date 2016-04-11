# -*- coding: utf-8; -*-
import unittest
import time

from fb_api import FBBot
from gg_api import GGBot
from gg_fetcher import GGFetcher
from gg_matcher import GGMatcher
from fb_fetcher import FBFetcher
from fb_searcher import FBSearcher

__author__ = "Wen-Hao Lee"
__email__ = "wing3s@gmail.com"
__copyright__ = "Copyright 2014, Numnum"


class FBBotTestCase(unittest.TestCase):
    def setUp(self):
        self.fb_bot = FBBot()

    def tearDown(self):
        pass

    def testFetchUserName(self):
        resp = self.fb_bot.fetch(100000818222236)
        assert resp['username'] == 'wing3s'

    def testFetchCategoryName(self):
        resp = self.fb_bot.fetch(470781916349719)
        assert resp['category_list'][0]['name'] == "Fondue Restaurant"

    def testSearch(self):
        params = {
            'q': 'coffee',
            'type': 'place',
            'center': '37.76,-122.427',
            'distance': 1000}
        resp = self.fb_bot.search(params)
        assert resp[0]['category'] == 'Local business'

    def testSearchPlace(self):
        result = self.fb_bot._search_place('restaurant', 25.04, 121.51)
        names = [x['name'] for x in result]
        assert 'Pondok Pitaya Hotel And Restaurant' in names

    def testSearchRestaurants(self):
        result = self.fb_bot.search_restaurant(25.035, 121.569)
        names = [x['name'] for x in result]
        found = False
        for name in names:
            if 'Lawry' in name:
                found = True
        assert found


class GGBotTestCase(unittest.TestCase):
    def setUp(self):
        self.gg_bot = GGBot()

    def tearDown(self):
        pass

    def testFetch(self):
        resp = self.gg_bot.fetch(
            "CpQBjAAAAGsFtkhTZsXWQ4YaAQX68OL"
            "yKhVRGRupRmXTqE9iwDnAblXxeasK9a"
            "1h2Z3CEw3olLEPF5gPIPlX4xiCc17-oj"
            "tH3WAd0MApjA2WPPLG1RpokYSaKwQJno"
            "6MZrvkqI4snTsVDhckQsWRN2y3jUm49b"
            "_aDNdDqpEfuJNCQ0k5NN4oPe19wpqe7U0"
            "TyDXYYWshOhIQzDymLziVOlAVYVYO6RGQF"
            "hoUAVcqXPyiFkG1ABx6ySG7u0iTVY0")
        ggid = "2a9edf0faa231d917726ac14622a4a464691c15a"
        assert resp['id'] == ggid

    def testSearchNearby(self):
        resp = self.gg_bot.search_nearby(
            "麥味登林口信義店",
            "restaurant",
            25.082706,
            121.374712)
        ggid = "2a9edf0faa231d917726ac14622a4a464691c15a"
        assert resp[0]['id'] == ggid


class FBSearcherTestCase(unittest.TestCase):
    def setUp(self):
        self.fb_searcher = FBSearcher('dev')

    def testSearchLocations(self):
        updated = self.fb_searcher.search_locations(5)
        assert updated > 0


class FBFetcherTestCase(unittest.TestCase):
    def setUp(self):
        self.fb_fetcher = FBFetcher('dev')

    def testUpdateShops(self):
        updated = self.fb_fetcher.update_shops_info(3)
        assert updated == 3


class GGMatcherTestCase(unittest.TestCase):
    def setUp(self):
        self.gg_matcher = GGMatcher('dev')

    def testMatchShops(self):
        matched = self.gg_matcher.match_fb_shops(5)
        assert (matched > 1 and matched <= 5)


class GGFetcherTestCase(unittest.TestCase):
    def setUp(self):
        self.gg_fetcher = GGFetcher('dev')

    def testUpdateShops(self):
        updated = self.gg_fetcher.update_shops_info(3)
        assert updated == 3


if __name__ == '__main__':
    unittest.main()
