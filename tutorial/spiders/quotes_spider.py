import scrapy
from scrapy import signals
from urllib import parse
import json
import os

class QuotesSpider(scrapy.Spider):
    name = 'quotes'

    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    def parse(self, response):
        division_by_zero = 1 / 0
        for quote in response.css('div.quote'):
            yield {
                #'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        
class AuthorSpider(scrapy.Spider):
    name = 'author'

    start_urls = ['http://quotes.toscrape.com/']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AuthorSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        yield from response.follow_all(response.css('.author + a'), self.parse_author)
        yield from response.follow_all(response.css('li.next a'), self)

    def spider_closed(self, spider):
        spider.logger.info('My Spider closed')

    def parse_author(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()
        
        yield {
            'name': extract_with_css('h3.author-title::text'),
            'birthdate': extract_with_css('author-born-date::text'),
            #'bio': extract_with_css('.author-description::text'),
        }

class UdemySpider(scrapy.Spider):

    name = 'udemy'

    http_user = os.getenv("UDEMY_USER_ID")
    http_pass = os.getenv("UDEMY_USER_PASS")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_requests(self):
        # TODO handle proxies
        url =  f"https://www.udemy.com/api-2.0/courses/"
        yield scrapy.Request(url, method='GET', callback=self.parse)

    def parse(self, response):
        js = json.loads(response.text)
        for course in js['results']:
            yield {'title': course['title']}
