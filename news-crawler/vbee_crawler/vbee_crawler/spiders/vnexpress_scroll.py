#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import os
import json
import csv
import pandas as pd 
from bs4 import BeautifulSoup
import re
class VnExpressScroll(scrapy.Spider):
    name = "vnexpress_scroll"
    page_limit = None
    start_urls = ['https://vnexpress.net/microservice/gocnhinpaging/category_id/1003450/page/0',]
    category_counter = {}

    def __init__(self, topic=None, start_url=None):
        
        # Tạo thư mục
        if not os.path.exists(self.name):
            os.mkdir(self.name)

        if start_url:
            self.start_urls = [start_url]
        self.topic = topic

    # def parse_scroll(self, response):
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        if self.topic == 'goc-nhin':
            data = json.loads(response.text)
            list_news = []
            if data['data']:
                for article in data['data']:
                    list_news.append(article['share_url'])
                csv_writer = csv.writer(open(f'{self.name}/{self.topic}.csv', 'a+', encoding='utf-8'))
                for link in list_news:
                    csv_writer.writerow([link, self.topic])

                next_page = data['page']
                yield scrapy.Request(f'https://vnexpress.net/microservice/gocnhinpaging/category_id/1003450/page/{next_page}', callback=self.parse)
        
        if self.topic == 'tam-su':
            data = json.loads(response.text)
            if data['html'] != '':
                html_doc = data['html']
                soup = BeautifulSoup(html_doc, 'html.parser')
                list_news = []
                articles = soup.find_all(name='h3', attrs={'class': 'title-news'})
                for article in articles:
                    list_news.append(article.a.get('href'))

                csv_writer = csv.writer(open(f'{self.name}/{self.topic}.csv', 'a+', encoding='utf-8'))
                for link in list_news:
                    csv_writer.writerow([link, self.topic])
                
            if 'message' not in data:
                next_page = data['page']
                print('next_page', next_page)
                yield scrapy.Request(f'https://vnexpress.net/ajax/listcategory/category_id/1001014/page/{next_page}', callback=self.parse)
    # def extract_next_page_url(self, response):
    #     try:
    #         return response.css("a.next-page").attrib['href']
    #     except:
    #         return None
