import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from ersparniskasse.items import Article


class ErsparniskasseSpider(scrapy.Spider):
    name = 'ersparniskasse'
    start_urls = ['https://www.ersparniskasse.ch/news-uebersicht/']

    def parse(self, response):
        articles = response.xpath('//div[@class="mp-span9 motopress-span"]/div[descendant::a[@class="btn-white btn-home btn"]]')
        for article in articles:
            link = article.xpath('.//a[@class="btn-white btn-home btn"]/@href').get()
            date = article.xpath('.//p/text()').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//div[@class="nav-next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1//text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="container-content format-text"]//div[@class="mp-span9 motopress-span"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
