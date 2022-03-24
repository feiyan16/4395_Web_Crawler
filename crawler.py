import sys_color as write
import scrapy
import sys


class RedditSpider(scrapy.Spider):
    name = 'Reddit-Movies'
    # start_urls = ['https://old.reddit.com/r/movies/']
    start_urls = ['https://old.reddit.com/search?q=the+batman&count=22&after=t3_tjkf1z']
    counter = 0
    urls = []

    # def parse(self, response, **kwargs):
    #     links = [a for a in response.xpath('//a[contains(@data-event-action, "title")]/@href').getall()]
    #     for url in links:
    #         if 'reddit' not in url:
    #             if 'https://' in url:
    #                 if '.png' not in url and '.gif' not in url and '.jpg' not in url:
    #                     yield scrapy.Request(url=url, callback=self.parse_page)

    def parse(self, response, **kwargs):
        write.stdout(f'current page {response.url}')
        links = [div for div in response.xpath('//div/div/a[contains(@class, "search-link may-blank")]/@href').getall()]
        for url in links:
            if 'redd.it' not in url and 'reddit' not in url and 'twitter' not in url:
                if '.png' not in url and '.gif' not in url and '.jpg' not in url:
                    yield scrapy.Request(url=url, callback=self.parse_page)

        yield from self.go_to_next_page(response)

    def go_to_next_page(self, response):
        next_page = response.xpath('//a[contains(@rel, "nofollow next")]/@href').get()
        if next_page:
            write.stdout(f'Going to next page {next_page}')
            yield scrapy.Request(url=next_page, callback=self.parse)
        else:
            write.stderr('No Next Page')

    def parse_page(self, response):
        if self.counter == 20:  # stopping condition, kills remaining threads
            write.stderr(f'link count = {self.counter}')
            sys.exit(0)
        write.stdout(f'Parsing {response.url}...')
        texts = self.scrape(response)  # scrape for texts on page
        if texts:
            filename = f'scraped_texts/url_{self.counter}.txt'
            file = open(filename, 'w')
            file.write(texts)
            write.stdok(f'SUCCESS: {response.url} written successfully as {filename}')

    def scrape(self, response):
        body = ''
        texts = [t for t in response.xpath('//title/text()').getall()]
        texts += [p for p in response.xpath('//p/text()').getall()]
        if len(texts) >= 10:  # Minimum amount of information needed
            for text in texts:
                body += (text + '\n')
            self.counter += 1
        else:
            write.stdwarn(f'{response.url} does not have enough data')
        return body
