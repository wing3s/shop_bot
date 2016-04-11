# cover picture
# restaurant types

# -*- coding=UTF-8 -*-
import argparse
import json
import re

from sqlalchemy import exc, func
from helper import get_logger, get_session, timeit
from models import FBShop, FBShopType
from fb_api import FBBot

__author__ = "Wen-Hao Lee"
__email__ = "wing3s@gmail.com"
__copyright__ = "Copyright 2014, Numnum"

logger = get_logger('fb_fetcher', __file__)


class FBFetcher(object):
    def __init__(self, env):
        self.fb_bot = FBBot()
        self.session = get_session(env)

    @timeit(logger)
    def fetch_new_shops(self, limit=None):
        fb_shops = (
            self.session.query(FBShop)
            .filter(FBShop.name == None)
            .order_by('update_ts').limit(limit).all())
        processed = 0
        for fb_shop in fb_shops:
            processed += self._fetch_info(fb_shop)
        logger.info(
            "Try to fetch %d new fb_shops info, %d fetched"
            % (len(fb_shops), processed))
        return processed

    @timeit(logger)
    def update_shops_info(self, limit=None):
        fb_shops = (
            self.session.query(FBShop)
            .order_by('update_ts').limit(limit).all())
        processed = 0
        for fb_shop in fb_shops:
            processed += self._fetch_info(fb_shop)
        logger.info(
            "Try to update %d fb_shops info, %d updated"
            % (len(fb_shops), processed))
        return processed

    @timeit(logger)
    def update_shops_rating(self, limit=None):
        fb_shops = (
            self.session.query(FBShop)
            .filter(FBShop.name != None)
            .order_by('update_ts').limit(limit).all())
        processed = 0
        for fb_shop in fb_shops:
            processed += self._fetch_rating(fb_shop)
        logger.info(
            "Try to update %d fb_shops rating, %d updated"
            % (len(fb_shops), processed))
        return processed

    def update_shop_info(self, fbid):
        fb_shop = self.session.query(FBShop).filter_by(fbid=int(fbid)).first()
        if not fb_shop:
            logger.error("fbid: %s Not found!" % fbid)
            return 0
        return self._fetch_info(fb_shop)

    def update_shop_rating(self, fbid):
        fb_shop = self.session.query(FBShop).filter_by(fbid=int(fbid)).first()
        if not fb_shop:
            logger.error("fbid: %s Not found!" % fbid)
            return 0
        return self._fetch_rating(fb_shop)

    def _fetch_info(self, fb_shop):
        fb_shop.update_ts = func.current_timestamp()

        info = self.fb_bot.fetch(fb_shop.fbid)
        if not info:
            logger.warning(
                "fbid: %s FB API GraphMethodException" % fb_shop.fbid)
            try:
                self.session.commit()
            except exc.SQLAlchemyError as err:
                self.session.rollback()
                logger.error(err)
            return 0

        old_fbid = fb_shop.fbid
        new_fbid = info.get('id')
        if old_fbid != int(new_fbid):
            existing_fb_shop = self.session.query(FBShop).filter_by(
                fbid=int(new_fbid)).first()
            if existing_fb_shop:
                self.session.delete(fb_shop)
                try:
                    self.session.commit()
                except exc.SQLAlchemyError as err:
                    self.session.rollback()
                    logger.error(err)
                fb_shop = existing_fb_shop

            fb_shop.old_fbid = old_fbid
            fb_shop.fbid = new_fbid
            logger.warning(
                "Set fbid %s(old) to new fbid %s"
                % (fb_shop.old_fbid, fb_shop.fbid))

        location = info.get('location', {})
        hours = info.get('hours', None)
        desc = info.get('desc', None)
        phone = info.get('phone', None)
        zipcode_str = location.get('zip')

        fb_shop.name = info.get('name')
        fb_shop.desc = info.get('description')
        fb_shop.website = info.get('website')
        fb_shop.address = location.get('street')
        fb_shop.city = location.get('city')
        fb_shop.lat = round(float(location.get('latitude', 0.0)), 7)
        fb_shop.lon = round(float(location.get('longitude', 0.0)), 7)
        fb_shop.likes = info.get('likes', 0)
        fb_shop.checkins = info.get('checkins', 0)
        fb_shop.talking = info.get('talking_about_count', 0)
        if hours:
            fb_shop.hours = json.dumps(hours, ensure_ascii=False)
        if desc:
            fb_shop.desc = desc.strip()
        if phone:
            fb_shop.phone = phone.strip()
        if zipcode_str:
            zipcode_str = re.sub("[^0-9]", "", zipcode_str)
            if len(zipcode_str) > 0:
                fb_shop.zipcode = int(zipcode_str)

        try:
            self.session.commit()
            status = 1
        except exc.SQLAlchemyError as err:
            self.session.rollback()
            logger.error(err)
            status = 0

        categories = info.get('category_list', None)
        if categories:
            self._save_categories(fb_shop.fbid, categories)
        return status

    def _save_categories(self, fbid, categories):
        added = 0
        for category in categories:
            type_ = category.get('name')
            existing_fb_shop_type = self.session.query(FBShopType).filter_by(
                fbid=int(fbid), type_=type_).first()
            if not existing_fb_shop_type:
                fb_shop_type = FBShopType(fbid=int(fbid), type_=type_)
                try:
                    self.session.add(fb_shop_type)
                    self.session.commit()
                except exc.SQLAlchemyError as err:
                    self.session.rollback()
                    logger.error(err)
                added += 1
        return added


    def _fetch_rating(self, fb_shop):
        info = self.fb_bot.fetch(fb_shop.fbid)
        if not info:
            logger.error(
                "fbid: %s FB API GraphMethodException" % fb_shop.fbid)
            return 0

        fb_shop.update_ts = func.current_timestamp()
        fb_shop.likes = info.get('likes', 0)
        fb_shop.checkins = info.get('checkins', 0)
        fb_shop.talking = info.get('talking_about_count', 0)
        try:
            self.session.commit()
            status = 1
        except exc.SQLAlchemyError as err:
            self.session.rollback()
            logger.error(err)
            status = 0
        return status


def main():
    parser = argparse.ArgumentParser(
        description="Fetch fb shops or update ratings")
    parser.add_argument(
        '-e', '--env', help='environment in dev/stage/prod', required=True)
    parser.add_argument(
        '-l', '--limit', help='limit num of locations to search', default=500)
    parser.add_argument(
        '-m', '--method', help='method in new/info/rating', required=True)
    args = parser.parse_args()

    fb_fetcher = FBFetcher(args.env)
    if args.method == 'new':
        fb_fetcher.fetch_new_shops(args.limit)
    elif args.method == 'info':
        fb_fetcher.update_shops_info(args.limit)
    elif args.method == 'rating':
        fb_fetcher.update_shops_rating(args.limit)

if __name__ == '__main__':
    main()