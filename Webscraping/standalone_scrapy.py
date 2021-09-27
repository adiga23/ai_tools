import scrapy
from scrapy.crawler import CrawlerProcess

class MySpider(scrapy.Spider):
    # Your spider definition
    name = 'countries'
    allowed_domains = ['www.worldometers.info']
    start_urls = ['https://www.worldometers.info/world-population/population-by-country/']

    def parse(self, response):
        countries = response.xpath("//td/a")
        #Get the first country
        # name = countries[0].xpath(".//text()").get()
        # link = countries[0].xpath(".//@href").get()
        # yield response.follow(url=link,callback=self.parse_country,meta={'country_name':name})

        for country in countries:
            name = country.xpath(".//text()").get()
            link = country.xpath(".//@href").get()
            yield response.follow(url=link,callback=self.parse_country,meta={'country_name':name})

    def parse_country(self, response):
        name = response.request.meta['country_name']
        tables = response.xpath("//table[@class='table table-striped table-bordered table-hover table-condensed table-list']")
        rows = tables[1].xpath(".//tr/td")
        ## Get population of latest year
        year = rows[0].xpath(".//text()").get()
        population = rows[1].xpath(".//text()").get()
        print(f"Adiga {name} {year} {population}")

        yield {"country" : name,
               "year" : year,
               "population":population}

process = CrawlerProcess({'LOG_LEVEL': 'WARNING'})
process.crawl(MySpider)
process.start() # the script will block here until the crawling is finished
