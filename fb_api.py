import os
import requests
import time
import ConfigParser
import logging
import logging.config

from requests.exceptions import RequestException
from helper import get_logger, base_path

config = ConfigParser.ConfigParser()
config.read(os.path.join(base_path, 'config.ini'))
logger = get_logger('fb_api', __file__)

__author__ = "Wen-Hao Lee"
__email__ = "wing3s@gmail.com"
__copyright__ = "Copyright 2014, Numnum"


class FBBot(object):
    graph_url = "https://graph.facebook.com"
    cooldown = 120  # sec
    search_radius = 500  # m

    def search_restaurant(self, lat, lon):
        restaurants = self._search_place('restaurant', lat, lon)
        steakhouses = self._search_place('steakhouse', lat, lon)
        bars = self._search_place('bar', lat, lon)
        return restaurants + steakhouses + bars

    def _search_place(self, query, lat, lon):
        params = {
            'q': query,
            'type': 'place',
            'center': '%s,%s' % (lat, lon),
            'distance': self.search_radius,
            'limit': 500,
            'offset': 0
        }
        return self.search(params)

    def search(self, params):
        params['access_token'] = "{app_id}|{app_key}".format(
            app_key=config.get('fbAPI', 'key'),
            app_id=config.get('fbAPI', 'id'))
        try:
            r = requests.get(
                "%s/%s" % (self.graph_url, 'search'),
                params=params)
            resp = r.json()
            if r.status_code != 200:
                resp_err = resp.get('error')
                err_code = resp_err.get('code')
                if err_code == 4:
                    logger.warning(
                        'Reach limit, cooldown %ds' % self.cooldown)
                    time.sleep(self.cooldown)
                    return self.search(params)
                else:
                    logger.error(resp)
                    return None
            return resp['data']
        except RequestException as err:
            logger.error(err)

    def fetch(self, fbid):
        try:
            r = requests.get("%s/%s" % (self.graph_url, fbid))
            resp = r.json()
            if r.status_code != 200:
                resp_err = resp.get('error')
                err_code = resp_err.get('code')
                if err_code == 4:
                    logger.warning(
                        'Reach limit, cooldown %ds' % self.cooldown)
                    time.sleep(self.cooldown)
                    return self.fetch(fbid)
                elif err_code == 21:
                    err_msg = resp_err.get('message')
                    new_fbid_pt = 'page ID'
                    new_fbid = err_msg[
                        err_msg.index(new_fbid_pt)+len(new_fbid_pt)+1:
                        err_msg.index('.')]
                    logger.warning(
                        'Get new fbid %s for %s' % (new_fbid, fbid))
                    return self.fetch(new_fbid)
                else:
                    logger.error([resp, r.url])
                    return None
            return resp
        except RequestException as err:
            logger.error(err)