import scrapy


class CountriesSpider(scrapy.Spider):
    name = 'countries'
    allowed_domains = ['www.worldometers.info']
    start_urls = ['https://www.worldometers.info/world-population/population-by-country/']

    def parse(self, response):
        countries = response.xpath("//td/a")
        ## Get the first country
        name = countries[0].xpath(".//text()").get()
        link = countries[0].xpath(".//@href").get()
        yield response.follow(url=link,callback=self.parse_country,meta={'country_name':name})
        # for country in countries:
            # name = country.xpath(".//text()").get()
            # link = country.xpath(".//@href").get()
#
            # yield response.follow(url=link,callback=parse_country,meta={'country_name':name})

    def parse_country(self, response):
        name = response.request.meta['country_name']
        tables = response.xpath("//table[@class='table table-striped table-bordered table-hover table-condensed table-list']")
        rows = tables[1].xpath(".//tr/td")
        ## Get population of latest year
        year = rows[0].xpath(".//text()").get()
        population = rows[1].xpath(".//text()").get()
        yield {"country" : name,
               "year" : year,
               "population":population}
