# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class LoggingHandler:
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

class TutorialPipeline(LoggingHandler):

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_item(self, item, spider):
        self.log.info(f"Got item: {item} from spider: {spider}")
        raise DropItem
        #return item

class SecondPipeline(LoggingHandler):
    def process_item(self, item, spider):
        self.log.info(f"Got item: {item} from spider: {spider}")
        return item
