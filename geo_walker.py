# -*- coding=UTF-8 -*-
import os
import json
import argparse

from sqlalchemy import exc
from helper import get_logger, base_path, get_session
from models import Track

__author__ = "Wen-Hao Lee"
__email__ = "wing3s@gmail.com"
__copyright__ = "Copyright 2014, Numnum"

logger = get_logger('geo_walker', __file__)


class CityWalker(object):
    rad = 500  # m

    def __init__(self, area, env):
        assert area in ['small', 'medium', 'large']
        area_turns = {
            'small': 10,
            'medium': 50,
            'large': 120}
        self.total_turns = area_turns[area]
        self.session = get_session(env)

    def load(self, file_name):
        file_fullpath = os.path.join(base_path, 'data', file_name)
        city_data = json.load(open(file_fullpath))
        self.cities = city_data['cities']

    def walk_all_cities(self):
        while self.cities:
            self.walk_city()

    def walk_city(self, city_name=None):
        if city_name:
            for city in self.cities:
                if city['name'].encode('UTF-8') == city_name:
                    self._circle_walk(city)
                    self.cities.remove(city)
        else:
            city = self.cities.pop()
            self._circle_walk(city)

    def _circle_walk(self, city):
        logger.info("Start walk %s city" % city['name'])
        cursor = [city['lat'], city['lon']]
        directions = ['up', 'right', 'down', 'left']
        direction_gap = [
            [0.0091,  0.0],
            [0.0,  0.0095],
            [-0.009, 0.0],
            [0.0, -0.0095]]
        direction_range = 1  # steps
        direction_index = 0

        for i in range(1, self.total_turns):
            for step in range(1, direction_range):
                cursor = [x+y for x, y in zip(
                    cursor, direction_gap[direction_index])]
                self._save_spot(cursor)
            direction_index += 1
            if direction_index == len(directions):
                direction_index = 0
            if directions[direction_index] in ['up', 'down']:
                direction_range += 1

    def _save_spot(self, cursor):
        cursor = [round(x, 6) for x in cursor]
        lat = cursor[0]
        lon = cursor[1]
        track = self.session.query(Track).filter_by(lat=lat, lon=lon).first()
        if not track:
            track = Track(lat=lat, lon=lon, rad=self.rad, found=0, saved=0)
            try:
                self.session.add(track)
                self.session.commit()
            except exc.SQLAlchemyError as err:
                session.rollback()
                logger.error(err)


def main():
    parser = argparse.ArgumentParser(description="Build searching tracks")
    parser.add_argument(
        '-e', '--env', help='environment in dev/stage/prod', required=True)
    parser.add_argument(
        '-s', '--size', help='set size small/medium/large', default='large')
    args = parser.parse_args()
    city_walker = CityWalker(args.size, args.env)
    city_walker.load('taiwan_cities.json')

    if args.env == 'dev':
        city_walker.walk_city("台北市")
    elif args.env == 'stage':
        city_walker.walk_all_cities()
    elif args.env == 'prod':
        city_walker.walk_all_cities()


if __name__ == '__main__':
    main()