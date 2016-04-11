from sqlalchemy import Column, ForeignKey, Integer, String, Float, TIMESTAMP, BigInteger
from sqlalchemy.ext.declarative import declarative_base

__author__ = "Wen-Hao Lee"
__email__ = "wing3s@gmail.com"
__copyright__ = "Copyright 2014, Numnum"

Base = declarative_base()


class Track(Base):
    __tablename__ = 'track'

    id_ = Column('id', Integer, primary_key=True)
    lat = Column('lat', Float(asdecimal=True))
    lon = Column('lon', Float(asdecimal=True))
    rad = Column('rad', Integer)
    found = Column('found', Integer)
    saved = Column('saved', Integer)
    update_ts = Column('update_ts', TIMESTAMP)


class FBShop(Base):
    __tablename__ = 'fb_shop'

    fbid    = Column('fbid', BigInteger, primary_key=True)
    name    = Column('name', String(100))
    desc    = Column('desc', String(900))
    phone   = Column('phone', String(14))
    website = Column('website', String(300))
    address = Column('address', String(300))
    city    = Column('city', String(20))
    lat     = Column('lat', Float(asdecimal=True))
    lon     = Column('lon', Float(asdecimal=True))
    zipcode = Column('zipcode', Integer)
    hours   = Column('hours', String(900))
    likes   = Column('likes', Integer)
    checkins    = Column('checkins', Integer)
    talking     = Column('talking', Integer)
    price       = Column('price', Integer) 
    track_id    = Column('track_id', Integer)
    old_fbid    = Column('old_fbid', BigInteger)
    ggid        = Column('ggid', String(50)) 
    update_ts   = Column('update_ts', TIMESTAMP)


class GGShop(Base):
    __tablename__ = 'gg_shop'

    ggid    = Column('ggid', String(50), primary_key=True)
    name    = Column('name', String(100))
    phone   = Column('phone', String(14))
    address = Column('address', String(300))
    city    = Column('city', String(20))
    lat     = Column('lat', Float(asdecimal=True))
    lon     = Column('lon', Float(asdecimal=True))
    zipcode = Column('zipcode', Integer)
    reference = Column('reference', String(150))
    update_ts = Column('update_ts', TIMESTAMP)

class FBShopType(Base):
    __tablename__ = 'fb_shop_type'

    fbid = Column('fbid', BigInteger, primary_key=True)
    type_ = Column('type', String(50), primary_key=True)