# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy import signals


import json
import codecs

from collections import OrderedDict
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.exceptions import DropItem
from scrapy import settings


class JsonWithEncodingPipeline(object):

    def __init__(self):
    	dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.file = codecs.open('data_utf8.json', 'w+')

    def process_item(self, item, spider):
        line = json.dumps(OrderedDict(item), ensure_ascii=False, sort_keys=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()
