# 711adjSys
711groupの勉強のため、簡単な精算システム

## 動作環境
* OS

自分のPCに応じる
* DB


select version(); -> 5.7.21
* server


python:Python 2.7.10

その他python package:flask(サーバー用)、mysql(DB用)

## DDL

dbname:seisan

```
CREATE TABLE `user_mst` (
  `id` int(11) NOT NULL,
  `name` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

CREATE TABLE `pay_biz` (
  `pay_id` int(11) NOT NULL AUTO_INCREMENT,
  `pay_payer` int(11) NOT NULL,
  `pay_for_users` varchar(20) NOT NULL,
  `pay_content` varchar(80) NOT NULL,
  `pay_amount` int(11) NOT NULL,
  `regist_date` datetime NOT NULL,
  PRIMARY KEY (`pay_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8


CREATE TABLE `adjustment_event` (
  `event_id` int(11) NOT NULL AUTO_INCREMENT,
  `detail_ids` varchar(500) NOT NULL,
  `event_amount` int(11) NOT NULL,
  `event_date` datetime NOT NULL,
  `event_from` int(11) NOT NULL,
  `event_to` int(11) NOT NULL,
  PRIMARY KEY (`event_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8

CREATE TABLE `adjustment_detail` (
  `ad_detail_id` int(11) NOT NULL AUTO_INCREMENT,
  `pay_id` int(11) NOT NULL,
  `ad_amount` int(11) NOT NULL,
  `ad_from` int(11) NOT NULL,
  `ad_to` int(11) NOT NULL,
  `ad_date` datetime DEFAULT NULL,
  `ad_done` int(1) NOT NULL,
  PRIMARY KEY (`ad_detail_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8



```
