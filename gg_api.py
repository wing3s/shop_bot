# -*- coding: utf-8; -*-
import os
import time
import requests
import ConfigParser

from requests.exceptions import RequestException
from helper import get_logger, base_path

__author__ = "Wen-Hao Lee"
__email__ = "wing3s@gmail.com"
__copyright__ = "Copyright 2014, Numnum"

config = ConfigParser.ConfigParser()
config.read(os.path.join(base_path, 'config.ini'))
logger = get_logger('gg_api', __file__)


class GGBot(object):
    map_url = "https://maps.googleapis.com/maps/api/place"
    cooldown = 180  # sec
    search_radius = 1200  # m

    def search_nearby(self, keyword, type_, lat, lon):
        nearby_url = "%s/%s" % (self.map_url, "nearbysearch/json")
        params = {
            'keyword': keyword,
            'location': "%s,%s" % (lat, lon),
            'radius': self.search_radius,
            'language': "zh-TW",
            'type': type_,
            'sensor': "false"
        }
        return self.request(nearby_url, params)

    def fetch(self, reference):
        fetch_url = "%s/%s" % (self.map_url, "details/json")
        params = {
            'reference': reference,
            'language': "zh-TW",
            'sensor': 'false'
        }
        return self.request(fetch_url, params)

    def request(self, url, params):
        params['key'] = config.get('googleMapAPI', 'key')
        try:
            r = requests.get(url, params=params)
            resp = r.json()
            status = resp['status']

            if status == 'OVER_QUERY_LIMIT':
                logger.warning('Reach limit, cooldown %ds' % self.cooldown)
                time.sleep(self.cooldown)
                return self.request(url, params)
            elif status == 'ZERO_RESULTS':
                logger.warning(
                    "Foud 0 result for %s" % params.get('keyword'))
                return None
            elif status != 'OK':
                logger.error(
                    "Status: %s for %s, request: %s "
                    % (status, params.get('keyword'), r.url))
                return None

            result = resp.get('results', None)
            if not result:
                result = resp.get('result', None)
            return result
        except RequestException as err:
            logger.error(err)