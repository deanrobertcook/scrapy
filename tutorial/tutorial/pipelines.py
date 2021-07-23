# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from itemadapter import ItemAdapter


class TutorialPipeline:


    def process_item(self, item, spider):
        logging.info(f"Got item: {item} from spider: {spider}")
        return item
