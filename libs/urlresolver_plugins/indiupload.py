import re
from urlresolver import common
from urlresolver.plugins.lib import helpers
from urlresolver.resolver import UrlResolver, ResolverError


class IndiShareResolver(UrlResolver):
    name = "IndiShare"
    domains = ['dl1.indishare.in']
    pattern = '(?://|\.)(dl1\.indishare\.in)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content
        data = helpers.get_hidden(html, form_id='F1')
        headers['Cookie'] = response.get_headers(as_dict=True).get('Set-Cookie', '')
        html = self.net.http_POST(response.get_url(), headers=headers, form_data=data).content
        url = re.search('id="direct_link">\s+<a href="(?P<url>[^"]+)"', html)

        if url:
            return url.group(1)
        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
