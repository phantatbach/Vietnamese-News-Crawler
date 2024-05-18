#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import os
import json
import csv
import re
class VnExpress(scrapy.Spider):
    name = "vnexpress"
    page_limit = None
    start_urls = []
    category_counter = {}

    def __init__(self, *args, **kwargs):
        super(VnExpress, self).__init__(*args, **kwargs)
        # Tạo thư mục
        if not os.path.exists(self.name):
            os.mkdir(self.name)

        with open(f'topic_links/{self.name}.txt', 'r') as f:
            # self.start_urls = f.read().splitlines()
            for url in f.read().splitlines():
                if not url.startswith('#'):
                    self.start_urls.append(url)

        for url in self.start_urls:
            topic = url.split('/')[-1]
            self.category_counter[topic] = [0, 0]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # def parse_scroll(self, response):

    def parse(self, response):
        next_page_url = self.extract_next_page_url(response)
        # print('next_page_url', next_page_url)
        category = self.get_category_from_url(response.url)

        list_news = response.css("h3.title-news> a::attr(href)").getall()
        list_news += response.css("h2.title-news> a::attr(href)").getall()
        if category in self.category_counter:
            self.category_counter[category][0] = self.category_counter[category][0] + len(list_news)

        csv_writer = csv.writer(open(f'{self.name}/{category}.csv', 'a+', encoding='utf-8'))
        for link in list_news:
            csv_writer.writerow([link, category])

        if next_page_url is not None and '/' in next_page_url:
            self.category_counter[category][1] = self.category_counter[category][1] + 1
            # Đệ qui để crawl trang kế tiếp
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)
        else:
            return

    def extract_next_page_url(self, response):
        try:
            return response.css("a.next-page").attrib['href']
        except:
            return None
        
    def get_category_from_url(self, url):
        items = url.split('/')
        category = None
        if len(items) >= 4:
            category = re.sub(r'-p[0-9]+', '', items[3])
        return category