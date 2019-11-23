import re
import time

from urlresolver import common
from urlresolver.plugins.lib import helpers
from urlresolver.resolver import UrlResolver, ResolverError

import requests


class MegaUpResolver(UrlResolver):
    name = "megaup"
    domains = ['megaup.net']
    pattern = '(?://|\.)(megaup\.net)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        megaup_request = requests.session()
        page = megaup_request.get(web_url)
        html = page.text
        print(page.status_code)
        url = re.search("href='(?P<url>[^\']+)'>download now", html)

        if url:
            time.sleep(8)
            r = megaup_request.get(url.group(1), allow_redirects=False)
            print(r.status_code)
            if r.status_code == 302:
                return r.headers['Location']
        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
