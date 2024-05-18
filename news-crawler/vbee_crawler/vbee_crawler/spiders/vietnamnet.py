#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import os
import json
import csv
import re
class Vietnamnet(scrapy.Spider):
    name = "vietnamnet"
    start_urls = []
    category_counter = {}
    topics = []
    def __init__(self):
       
        # Tạo thư mục
        if not os.path.exists(self.name):
            os.mkdir(self.name)

        with open(f'topic_links/{self.name}.txt', 'r') as f:
            # self.start_urls = f.read().splitlines()
            for url in f.read().splitlines():
                if not url.startswith('#'):
                    self.start_urls.append(url)
                    self.topics.append(url.split('/')[-1])

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

        list_news = response.css('h3.vnn-title>a::attr(href)').getall()
        list_news += response.css('h2.vnn-title>a::attr(href)').getall()
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
            return response.css('li.pagination-next>a::attr(href)').get()
        except:
            return None
        
    def get_category_from_url(self, url):
        category = None
        for topic in self.topics:
            if topic in url:
                category = topic
                break
        return category