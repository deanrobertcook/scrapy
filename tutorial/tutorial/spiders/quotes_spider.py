import scrapy

class QuotesSpider(scrapy.Spider):
    name = 'quotes'

    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    def parse(self, response):
        getattr
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
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

    def parse(self, response):
        yield from response.follow_all(response.css('.author + a'), self.parse_author)
        yield from response.follow_all(response.css('li.next a'), self)

    def parse_author(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()
        
        yield {
            'name': extract_with_css('h3.author-title::text'),
            'birthdate': extract_with_css('author-born-date::text'),
            'bio': extract_with_css('.author-description::text'),
        }