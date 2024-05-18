"""
Get all category link from a news source
"""

import newspaper  

config = newspaper.Config()
config.fetch_images = False
config.memoize_articles = False
config.language = 'vi'

NEWS_SOURCES = ['https://lifestyle.zingnews.vn/']

news = newspaper.build(NEWS_SOURCES[0], config=config)
for category in news.category_urls():
    print(category)