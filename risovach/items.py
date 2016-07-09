import scrapy


class Mem(scrapy.Item):
    title = scrapy.Field()
    img_id = scrapy.Field()
    img_name = scrapy.Field()
