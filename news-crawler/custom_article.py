from typing_extensions import override
import requests 
import ssl
import urllib3

from newspaper import Article
from newspaper.network import _get_html_from_response, get_request_kwargs
from newspaper.configuration import Configuration
from newspaper.utils import extract_meta_refresh
from newspaper.article import ArticleDownloadState, log

def get_html_2XX_only_custom_ssl(url, config=None, response=None):
    """Consolidated logic for http requests from newspaper. We handle error cases:
    - Attempt to find encoding of the html by using HTTP header. Fallback to
      'ISO-8859-1' if not provided.
    - Error out if a non 2XX HTTP response code is returned.
    """
    config = config or Configuration()
    useragent = config.browser_user_agent
    timeout = config.request_timeout
    proxies = config.proxies
    headers = config.headers

    if response is not None:
        return _get_html_from_response(response)

    # response = requests.get(
    #     url=url, **get_request_kwargs(timeout, useragent, proxies, headers))
    with get_legacy_session() as s:
        response = s.get(url=url, **get_request_kwargs(timeout, useragent, proxies, headers))
    html = _get_html_from_response(response)

    if config.http_success_only:
        # fail if HTTP sends a non 2XX response
        response.raise_for_status()

    return html

def get_html_custom_ssl(url, config=None, response=None):
    """HTTP response code agnostic
    """
    try:
        return get_html_2XX_only_custom_ssl(url, config, response)
    except requests.exceptions.RequestException as e:
        log.debug('get_html() error. %s on URL: %s' % (e, url))
        return ''
    
class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session

class CustomArticle(Article):
    @override
    def download(self, input_html=None, title=None, recursion_counter=0):
        """Downloads the link's HTML content, don't use if you are batch async
        downloading articles

        recursion_counter (currently 1) stops refreshes that are potentially
        infinite
        """
        if input_html is None:
            try:
                html = get_html_2XX_only_custom_ssl(self.url, self.config)
            except requests.exceptions.RequestException as e:
                self.download_state = ArticleDownloadState.FAILED_RESPONSE
                self.download_exception_msg = str(e)
                log.debug('Download failed on URL %s because of %s' %
                          (self.url, self.download_exception_msg))
                return
        else:
            html = input_html

        if self.config.follow_meta_refresh:
            meta_refresh_url = extract_meta_refresh(html)
            if meta_refresh_url and recursion_counter < 1:
                return self.download(
                    input_html=get_html_custom_ssl(meta_refresh_url),
                    recursion_counter=recursion_counter + 1)

        self.set_html(html)
        self.set_title(title)

if __name__ == '__main__':
    article = CustomArticle('https://baotintuc.vn/am-thuc/viet-nam-tham-gia-trien-lam-thuc-pham-quoc-te-thuong-hai-2023-20230518170544562.htm')
    article.download()
    article.parse()
    print(article.title)
    print('------------------')
    print(article.text)
    print('------------------')
    print(article.tags)
    print('------------------')