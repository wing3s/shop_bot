# -*- coding=UTF-8 -*-
import argparse

from sqlalchemy import exc
from helper import get_logger, get_session, timeit
from models import FBShop, GGShop
from gg_api import GGBot

__author__ = "Wen-Hao Lee"
__email__ = "wing3s@gmail.com"
__copyright__ = "Copyright 2014, Numnum"

logger = get_logger('gg_matcher', __file__)


class GGMatcher(object):
    def __init__(self, env, match_type='restaurant'):
        self.gg_bot = GGBot()
        self.session = get_session(env)
        self.match_type = match_type

    @timeit(logger)
    def match_fb_shops(self, limit=None):
        fb_shops = (
            self.session.query(FBShop)
            .filter(FBShop.name != None)
            .filter(FBShop.ggid == None)
            .order_by('update_ts').limit(limit).all())
        processed = 0
        for fb_shop in fb_shops:
            processed += self._find_gg_shop(fb_shop)
        logger.info(
            "Try to match %d gg_shops for fb_shops, %d matched"
            % (len(fb_shops), processed))
        return processed

    def match_fb_shop(self, fbid):
        fb_shop = (self.session.query(FBShop)
            .filter_by(fbid=int(fbid)).first())
        if not fb_shop:
            logger.error("fbid: %s Not found!" % fbid)
            return 0
        return self._find_gg_shop(fb_shop)

    def _find_gg_shop(self, fb_shop):
        info = self.gg_bot.search_nearby(
            fb_shop.name,
            self.match_type,
            fb_shop.lat,
            fb_shop.lon)
        if not info or len(info) < 1:
            logger.warning("No gg_shop matched for %s fbid" % fb_shop.fbid)
            fb_shop.ggid = '0'
            try:
                self.session.commit()
            except exc.SQLAlchemyError as err:
                self.session.rollback()
                logger.error(err)
            return 0
        else:
            matched = info[0]
            ggid = matched.get('id')
            reference = matched.get('reference')

            gg_shop = self.session.query(GGShop).filter_by(ggid=ggid).first()
            if not gg_shop:
                gg_shop = GGShop(ggid=ggid, reference=reference)
            fb_shop.ggid = ggid
            try:
                self.session.add(gg_shop)
                self.session.commit()
            except exc.SQLAlchemyError as err:
                self.session.rollback()
                logger.error(err)
            return 1


def main():
    parser = argparse.ArgumentParser(description="Match fb to gg shops")
    parser.add_argument(
        '-e', '--env', help='environment in dev/stage/prod', required=True)
    parser.add_argument(
        '-l', '--limit', help='limit num of locations to search', default=500)
    args = parser.parse_args()

    gg_matcher = GGMatcher(args.env)
    gg_matcher.match_fb_shops(args.limit)


if __name__ == '__main__':
    main()