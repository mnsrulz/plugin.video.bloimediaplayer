import re
from urlresolver import common
from urlresolver.plugins.lib import helpers, jsunpack
from urlresolver.resolver import UrlResolver, ResolverError
import requests


class StreamWireResolver(UrlResolver):
    name = "streamwire"
    domains = ['streamwire.net']
    pattern = '(?://|\.)(streamwire\.net)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search("script type='text/javascript'>(eval.*?)</script", html, re.DOTALL)

        if r:
            html = jsunpack.unpack(r.group(1))
            src = re.search('src:"([^"]+)"', html)
            if src:
                return src.group(1) + helpers.append_headers(headers)

        raise ResolverError('Video cannot be located.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
