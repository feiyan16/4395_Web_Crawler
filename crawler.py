import sys

from scrapy.exceptions import CloseSpider
from scrapy import signals

import sys_color as write
import scrapy


class RedditSpider(scrapy.Spider):
    name = 'Reddit-Movies'
    start_urls = ['https://old.reddit.com/search?q=the+batman&count=22&after=t3_tjkf1z']  # URL page to start with
    counter = 0  # relevant link counter, used as a timer

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(RedditSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        spider.logger.info(f'RedditSpider closed: link count == {self.counter}')

    def parse(self, response, **kwargs):
        write.stdout(f'current page {response.url}')
        # gets list of links that are in the current url page
        links = [div for div in response.xpath('//div/div/a[contains(@class, "search-link may-blank")]/@href').getall()]
        # FILTER THE URLS:
        # URLs must not belong in reddit domain, not twitter because twitter doesn't
        # allow scraping, and url must not be a link to an image, because then there is not text to parse
        for url in links:
            if 'redd.it' not in url and 'reddit' not in url and 'twitter' not in url:
                if '.png' not in url and '.gif' not in url and '.jpg' not in url:
                    yield scrapy.Request(url=url, callback=self.parse_page)  # parse html for url page

        yield from self.go_to_next_page(response)  # go to the next page in the reddit forum/discussion

    def go_to_next_page(self, response):
        # Get the url for the next page by getting the href attribute value from the next page html button
        next_page = response.xpath('//a[contains(@rel, "nofollow next")]/@href').get()
        if next_page:  # if there is a next page
            write.stdout(f'Going to next page {next_page}')
            yield scrapy.Request(url=next_page, callback=self.parse)  # follow and call self.parse on the url again
        else:
            write.stderr('No Next Page')

    def parse_page(self, response):
        if self.counter == 20:
            sys.exit(0)
            raise CloseSpider(f'link count == {self.counter}')
        write.stdout(f'Parsing {response.url}...')
        body = self.scrape(response)  # scrape for texts on page
        if body:  # if body is not empty
            filename = f'scraped_texts/url_{self.counter}.txt'
            file = open(filename, 'w')
            file.write(body)  # write body out to a file
            write.stdok(f'SUCCESS: {response.url} written successfully as {filename}')

    def scrape(self, response):
        body = ''
        texts = [t for t in response.xpath('//title/text()').getall()]  # get the title of the url page
        texts += [p for p in response.xpath('//p/text()').getall()]  # get all texts from the HTML paragraph element
        if len(texts) >= 10:  # Minimum amount of information needed on url page
            for text in texts:
                body += (text + '\n')
            self.counter += 1  # increment relevant link counter
        else:
            write.stdwarn(f'{response.url} does not have enough data')
        return body
