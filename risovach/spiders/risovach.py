import functools
import urllib.request

import scrapy

from risovach.items import Mem


class RisovachSpider(scrapy.Spider):
    name = 'risovach'
    start_urls = ['http://risovach.ru/mem-generators']

    def __init__(self, *args, **kwargs):
        self.current_img = None
        self.img_id_counter = 1
        super().__init__(*args, **kwargs)

    def parse(self, response):
        # there're 22 pages of mems right now
        for page in range(2, 22):
            yield scrapy.Request('http://risovach.ru/mem-generators/{}'.format(page))

        for link in response.css('.generators .square a'):
            # full_url = response.urljoin(link.css('::attr(href)').extract_first())
            # we need to generate a URL by the mem name

            mem_name = link.css('::attr(href)').extract_first().split('/')[-1]

            if mem_name.isnumeric():
                mem_name = response.url.split('/')[-2]

            full_url = 'http://risovach.ru/memy/{}/all'.format(mem_name)

            img = response.urljoin(link.css('img::attr(src)').extract_first())
            img_name = img.split('/')[-1]
            img_name = img_name.split('?')[0]

            # !!! we already have images
            # print("Retrieving image {}".format(img))
            # urllib.request.urlretrieve(img, "imgs/{}".format(img_name))

            yield scrapy.Request(response.urljoin(full_url), functools.partial(self.parse_texts,
                                                                               img_name=img_name,
                                                                               img_id=self.img_id_counter,
                                                                               first_page=True))
            self.img_id_counter += 1

    def parse_texts(self, response, img_name=None, img_id=None, first_page=False):
        if first_page:
            # Go over all pages
            last_page = response.css('.paginate a::text')[-1].extract()

            for page in range(2, int(last_page) + 1):
                page_url = response.url + '/' + str(page)
                yield scrapy.Request(response.urljoin(page_url), functools.partial(self.parse_texts,
                                                                                   img_name=img_name,
                                                                                   img_id=img_id))

        for title in response.css('.unit-c img::attr(alt)').extract():
            yield Mem(title=title, img_name=img_name, img_id=img_id)
