import scrapy
from scrapy.crawler import CrawlerProcess

## Set this in the unix environment for printing the unicode characters
#setenv PYTHONIOENCODING UTF-8

class MySpider(scrapy.Spider):
    # Your spider definition
    name = 'countries'
    allowed_domains = ['web.archive.org']

    def start_requests(self):
        yield scrapy.Request(url='https://web.archive.org/web/20190225123327/https://www.tinydeal.com/specials.html',
                             callback=self.parse,
                             headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'})

    def parse(self, response):
        print(f"HEADER : {response.request.headers['User-Agent']}")
        products = response.xpath("//div[@class='p_box_wrapper']")
        for product in products:
            title = product.xpath(".//a[@class='p_box_title']/text()").get()
            price_resp = product.xpath(".//div[@class='p_box_price']")
            normal_price = price_resp.xpath(".//span[@class='normalprice fl']/text()").get()
            special_price = price_resp.xpath(".//span[@class='productSpecialPrice fl']/text()").get()
            print(f"Adiga {title} {normal_price} {special_price}")

        next_page=response.xpath("//a[@class='nextPage']/@href").get()
        if "page_num" in response.request.meta:
            counter = response.request.meta['page_num'] + 1
        else:
            counter = 1

        if next_page:
            print(f"Going to next page {next_page} {counter + 1}")
            yield scrapy.Request(url=next_page,
                                 callback=self.parse,
                                 meta={'page_num' : counter},
                                 headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'})


process = CrawlerProcess({'LOG_LEVEL': 'WARNING'},
                         {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'})
process.crawl(MySpider)
process.start() # the script will block here until the crawling is finished
