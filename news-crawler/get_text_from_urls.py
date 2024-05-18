"""
Using newspaper3k to parse text from list of crawled urls
"""

import time
import csv 
import os
import math
import re 
import argparse
from p_tqdm import p_map
import numpy as np
import newspaper
import custom_article
import pandas as pd

SAVE_FOLDER = 'data_crawled'
URLS_FOLDER = 'vbee_crawler/urls_crawled'
BATCH_SIZE = 10000
THREADS = 50
PMAP_CPUS = 10
# urls = df['url'].tolist()
# topic = df['category'][0]
def parse_text(article):
    try:
        article.parse()
    except Exception as e:
        print(e)
        return article.url, '', ''

    text = re.sub(r'\n\n', '\n', article.text)
    return article.url, article.title, text 
    # return article.url, article.title, article.text

def parse_articles(urls, topic, news, index):
    if os.path.exists(f'{SAVE_FOLDER}/{news}/{topic}_{index}.csv'):
        print('Skip already parsed articles')
        return 
    if news == 'baotintuc':
        articles = [custom_article.CustomArticle(url) for url in urls]
    else:
        articles = [newspaper.Article(url) for url in urls]
    start = time.perf_counter()
    newspaper.news_pool.set(articles, override_threads=THREADS)
    newspaper.news_pool.join()
    print(f'Download {len(urls)} articles took {time.perf_counter() - start} seconds')

    start = time.perf_counter()
    with open(f'{SAVE_FOLDER}/{news}/{topic}_{index}.csv', 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f, delimiter=',')
        csv_writer.writerow(['url', 'category', 'title', 'text'])

        results = p_map(parse_text, articles, num_cpus=PMAP_CPUS)
        for url, title, text in results:
            csv_writer.writerow([url, topic, title, text])
        # for a in articles:
        #     a.parse()
        #     text = re.sub(r'\n\n', '\n', a.text)
        #     csv_writer.writerow([a.url, topic, a.title, text])
    print(f'Parsed {len(urls)} articles in {time.perf_counter() - start} seconds')
    del articles

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--news', type=str, default='vnexpress')
    
    args = parser.parse_args()
    news = args.news
    os.makedirs(f'{SAVE_FOLDER}/{news}', exist_ok=True)
    for csv_file in os.listdir(f'{URLS_FOLDER}/{news}'):
        df = pd.read_csv(f'{URLS_FOLDER}/{news}/{csv_file}', names=["url", "category"])

        # remove duplicate urls
        df.drop_duplicates(subset=['url'], inplace=True)

        # get topic from file name
        topic = csv_file.split('/')[-1].split('.')[0]
        print(f'Parsing {topic}...')
        count = 0
        urls = df['url'].tolist()
        
        num_batches = math.ceil(len(urls) / BATCH_SIZE)

        for i in range(num_batches):
            urls_batch = urls[i*BATCH_SIZE:(i+1)*BATCH_SIZE]

            processed_urls = []
            for url in urls_batch:
                if news == 'vietnamnet' and not url.startswith('https://vietnamnet.vn'):
                    url = 'https://vietnamnet.vn' + url
                if news == 'suckhoedoisong' and not url.startswith('https://suckhoedoisong.vn'):
                    url = 'https://suckhoedoisong.vn' + url
                if news == 'vov' and not url.startswith('https://vov.vn'):
                    url = 'https://vov.vn' + url
                processed_urls.append(url)
                # if url.endswith('.html'):
                #     processed_urls.append(url)
            parse_articles(processed_urls, topic, news, i)
        print('Done!')