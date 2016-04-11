# -*- coding=UTF-8 -*-
import argparse

from sqlalchemy import exc, or_, func
from helper import get_logger, get_session, timeit
from models import Track, FBShop
from fb_api import FBBot

__author__ = "Wen-Hao Lee"
__email__ = "wing3s@gmail.com"
__copyright__ = "Copyright 2014, Numnum"

logger = get_logger('fb_searcher', __file__)


class FBSearcher(object):
    def __init__(self, env):
        self.fb_bot = FBBot()
        self.session = get_session(env)

    @timeit(logger)
    def search_locations(self, limit=None):
        locs = (
            self.session.query(Track)
            .order_by('update_ts').limit(limit).all())
        updated = 0
        for loc in locs:
            updated += self.search_location(loc)
        return updated

    def search_location(self, loc):
        shops = self.fb_bot.search_restaurant(loc.lat, loc.lon)
        loc.found = len(shops)
        updated = 0
        for shop in shops:
            updated += self._save_fb_shop(shop.get('id'), loc)
        logger.info(
            "Track_id: {track_id}  Found: {found}  Updated: {updated}".format(
                track_id=loc.id_,
                found=loc.found,
                updated=updated))

        loc.update_ts = func.current_timestamp()
        try:
            self.session.commit()
        except exc.SQLAlchemyError as err:
            self.session.rollback()
            logger.error(err)
        return updated

    def _save_fb_shop(self, fbid, loc):
        fb_shop = self.session.query(FBShop).filter(
            or_(FBShop.fbid == int(fbid), FBShop.old_fbid == int(fbid))).first()
        if not fb_shop:
            fb_shop = FBShop(fbid=int(fbid), track_id=loc.id_)
            try:
                loc.saved += 1
                self.session.add(fb_shop)
                self.session.commit()
            except exc.SQLAlchemyError as err:
                self.session.rollback()
                logger.error(err)
            return 1
        return 0


def main():
    parser = argparse.ArgumentParser(description="Search fb shops from tracks")
    parser.add_argument(
        '-e', '--env', help='environment in dev/stage/prod', required=True)
    parser.add_argument(
        '-l', '--limit', help='limit num of locations to search', default=500)
    args = parser.parse_args()

    fb_searcher = FBSearcher(args.env)
    fb_searcher.search_locations(args.limit)


if __name__ == '__main__':
    main()