# -*- coding: utf-8 -*-
import json
from binascii import crc32
from scrapy.exceptions import DropItem

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class TiebaPipeline(object):
    def __init__(self, filename):
        self.filename = filename

    @classmethod
    def from_crawler(cls, crawler):
        filename = crawler.settings.get('FILENAME')
        return cls(
                filename = crawler.settings.get('FILENAME')
                )

    def open_spider(self, spider):
        self.file = open(self.filename, 'wb')
        #self.file.write("{\"items\":[\n".encode('utf-8'))

    def close_spider(self, spider):
        if self.file is not None:
            #self.file.truncate(self.file.tell() - 2)
            #self.file.write("\n]}".encode('utf-8'))
            self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line.encode('utf-8'))
        return item

class DuplicatesPipeline(object):
    def __init__(self):
        self.thread_set = set()
    
    def process_item(self, item, spider):
        checksum = crc32(item['preview'].encode('utf-8'))
        if checksum in self.thread_set:
            raise DropItem("Duplicated content from %s" % item['author'])
        else:
            self.thread_set.add(checksum)
            return item
