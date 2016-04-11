# -*- coding=UTF-8 -*-
import argparse
import re

from sqlalchemy import exc, func
from helper import get_logger, get_session, timeit
from models import GGShop
from gg_api import GGBot

__author__ = "Wen-Hao Lee"
__email__ = "wing3s@gmail.com"
__copyright__ = "Copyright 2014, Numnum"

logger = get_logger('gg_fetcher', __file__)


class GGFetcher(object):

    def __init__(self, env):
        self.gg_bot = GGBot()
        self.session = get_session(env)

    @timeit(logger)
    def fetch_new_shops(self, limit=None):
        gg_shops = (
            self.session.query(GGShop)
            .filter(GGShop.name == None)
            .order_by('update_ts').limit(limit).all())
        processed = 0
        for gg_shop in gg_shops:
            processed += self._fetch_info(gg_shop)
        logger.info(
            "Try to fetch %d new gg_shops info, %d fetched"
            % (len(gg_shops), processed))
        return processed

    @timeit(logger)
    def update_shops_info(self, limit=None):
        gg_shops = (
            self.session.query(GGShop)
            .order_by('update_ts').limit(limit).all())
        processed = 0
        for gg_shop in gg_shops:
            processed += self._fetch_info(gg_shop)
        logger.info(
            "Try to update %d gg_shops info, %d updated"
            % (len(gg_shops), processed))
        return processed

    def update_shop_info(self, ggid):
        gg_shop = self.session.query(GGShop).filter_by(ggid=ggid).first()
        if not gg_shop:
            logger.error("ggid: %s Not found!" % ggid)
            return 0
        return self._fetch_info(gg_shop)

    def _fetch_info(self, gg_shop):
        gg_shop.update_ts = func.current_timestamp()

        info = self.gg_bot.fetch(gg_shop.reference)
        if not info:
            logger.warning('Can NOT retrieve gg_shop info for %s' % gg_shop.ggid)
            try:
                self.session.commit()
            except exc.SQLAlchemyError as err:
                self.session.rollback()
                logger.error(err)
            return 0

        location_comp = info.get('address_components', None)
        city = None
        zipcode = None
        if location_comp:
            for comp in location_comp:
                if "administrative_area_level_1" in comp['types']:
                    city = comp.get("long_name")
                elif "postal_code" in comp['types']:
                    zipcode_str = re.sub("[^0-9]", "", comp.get('long_name'))
                    if len(zipcode_str) > 0:
                        zipcode = int(zipcode_str)

        gg_shop.name = info.get('name')
        gg_shop.phone = info.get('formatted_phone_number')
        gg_shop.address = info.get('formatted_address')
        gg_shop.city = city
        gg_shop.lat = round(float(info['geometry']['location'].get('lat')), 7)
        gg_shop.lon = round(float(info['geometry']['location'].get('lng')), 7)
        gg_shop.zipcode = zipcode
        try:
            self.session.commit()
            status = 1
        except exc.SQLAlchemyError as err:
            self.session.rollback()
            logger.error(err)
            status = 0
        return status


def main():
    parser = argparse.ArgumentParser(description="Fetch gg shops or update")
    parser.add_argument(
        '-e', '--env', help='environment in dev/stage/prod', required=True)
    parser.add_argument(
        '-l', '--limit', help='limit num of locations to search', default=500)
    parser.add_argument(
        '-m', '--method', help='method in new/info', required=True)
    args = parser.parse_args()

    gg_fetcher = GGFetcher(args.env)
    if args.method == 'new':
        gg_fetcher.fetch_new_shops(args.limit)
    elif args.method == 'info':
        gg_fetcher.update_shops_info(args.limit)

if __name__ == '__main__':
    main()