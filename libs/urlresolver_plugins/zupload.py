import re
from urlresolver import common
from urlresolver.plugins.lib import helpers
from urlresolver.resolver import UrlResolver, ResolverError
import requests


class ZUploadResolver(UrlResolver):
    name = "zupload"
    domains = ['zupload.me']
    pattern = '(?://|\.)(zupload\.me)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        print('fetching zupload url: ' + web_url)
        zuploadsessionrequest = requests.session()
        page = zuploadsessionrequest.get(web_url)
        print(page.status_code)
        data = helpers.get_hidden(page.text, index=1)
        post_result = zuploadsessionrequest.post(page.url, data=data)
        url = re.search('class="link_button".*href=["\'](?P<url>[^"\']+)', post_result.text)

        if url:
            return url.group(1)
        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
