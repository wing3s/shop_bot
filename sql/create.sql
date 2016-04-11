-- fb_track table
CREATE TABLE `track` (
  `id`        int(11)         unsigned NOT NULL AUTO_INCREMENT,
  `lat`       decimal(10,6)   NOT NULL,
  `lon`       decimal(10,6)   NOT NULL,
  `rad`       int(4)          unsigned NOT NULL,
  `found`     int(6)          unsigned NOT NULL,
  `saved`     int(6)          unsigned NOT NULL DEFAULT '0',
  `update_ts` timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY  `location`  (`lat`,`lon`),
  KEY         `update_ts` (`update_ts`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- fb restaurant
CREATE TABLE `fb_shop` (
  `fbid`      bigint(20)      unsigned NOT NULL,
  `name`      varchar(100)    DEFAULT NULL,
  `desc`      varchar(900)    DEFAULT NULL,
  `phone`     varchar(14)     DEFAULT NULL,
  `website`   varchar(300)    DEFAULT NULL,
  `address`   varchar(300)    DEFAULT NULL,
  `city`      varchar(20)     DEFAULT NULL,
  `lat`       decimal(10,7)   DEFAULT NULL,
  `lon`       decimal(10,7)   DEFAULT NULL,
  `zipcode`   int(20)         unsigned DEFAULT NULL,
  `hours`     varchar(900)    DEFAULT NULL,
  `likes`     int(8)          unsigned DEFAULT NULL,
  `checkins`  int(10)         unsigned DEFAULT NULL,
  `talking`   int(8)          unsigned DEFAULT NULL,
  `price`     int(1)          DEFAULT NULL,
  `track_id`  int(11)         unsigned NOT NULL,
  `old_fbid`  bigint(20)      unsigned DEFAULT NULL,
  `ggid`      varchar(50)     DEFAULT NULL,
  `update_ts` timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY `fb`        (`fbid`),
  KEY         `old_fbid`  (`old_fbid`),
  KEY         `ggid`      (`ggid`),
  KEY         `location`  (`lat`,`lon`),
  KEY         `name`      (`name`),
  KEY         `update_ts` (`update_ts`),
  KEY         `city`      (`city`),
  CONSTRAINT `track_id` FOREIGN KEY (`track_id`) REFERENCES `track` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- google restaurant
CREATE TABLE `gg_shop` (
  `ggid` varchar(50)        DEFAULT NULL,
  `name` varchar(100)       DEFAULT NULL,
  `phone` varchar(14)       DEFAULT NULL,
  `address` varchar(300)    DEFAULT NULL,
  `city` varchar(20)        DEFAULT NULL,
  `lat` decimal(10,7)       DEFAULT NULL,
  `lon` decimal(10,7)       DEFAULT NULL,
  `zipcode` int(20)         unsigned DEFAULT NULL,
  `reference` varchar(300)  NOT NULL,
  `update_ts` timestamp     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY `ggid` (`ggid`),
  KEY `location` (`lat`,`lon`),
  KEY `name` (`name`),
  KEY `reference` (`reference`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- restaurant_type
CREATE TABLE `fb_shop_type` (
  `fbid` bigint(20) unsigned NOT NULL,
  `type` varchar(50) NOT NULL,
  PRIMARY KEY (`fbid`,`type`),
  KEY `type` (`type`),
  CONSTRAINT `fb_shop_type` FOREIGN KEY (`fbid`) REFERENCES `fb_shop` (`fbid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

-- restaurant_pic
CREATE TABLE `shop_pic` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `fb_shop_id` int(11) unsigned NOT NULL,
  `pic` varchar(500) NOT NULL,
  `order` int(3) unsigned DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY 'shop_pic' ('fb_shop_id', 'pic'),
  KEY `fb_shop_id` (`fb_shop_id`),
  CONSTRAINT `fb_shop_pic` FOREIGN KEY (`fb_shop_id`) REFERENCES `fb_shop` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;