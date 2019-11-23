import sys
import time
from urllib import urlencode
from urlparse import urljoin
from urlparse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import requests
import json
import CommonFunctions
import os
from libs.bcp import BaseClassPlugin
common = CommonFunctions


class MovieRetina(BaseClassPlugin):
    name = "free spin wins"
    domains = ['freespinwins']
    pattern = r'(?://|\.)(freespinwins\.com)'

    def get_content(self, content_url):
        print('inside freespinwins dynamic module')
        if content_url.startswith('https://freespinwins'):
            return self.execute(content_url)
        else:
            return False

    def execute(self, content_url):
        movieList = []
        genre = 'movie'
        headers = {
            'User-Agent': 'Mozilla'
        }
        session_request = requests.session()

        page = session_request.get(content_url, headers=headers)
        page_form = common.parseDOM(page.text, 'form', attrs={"id": "go-link"})
        page_form_action = common.parseDOM(page.text, 'form', attrs={"id": "go-link"}, ret="action")[0]
        name_collection = common.parseDOM(page_form, 'input', ret='name')
        value_collection = common.parseDOM(page_form, 'input', ret='value')
        print('page form action')
        print(page_form_action)
        print('found the nv collection this time')
        print(name_collection)
        print(value_collection)
        payload = {}
        for n, v in zip(name_collection, value_collection):
            payload[str(n)] = str(v)
        print('post payload ready to post')
        print(payload)
        data_to_send = str(urlencode(payload))
        print('sending the data below')
        print(data_to_send)
        headers['x-requested-with'] = 'XMLHttpRequest'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        time.sleep(5)
        print('printing url to post')

        url_to_post = urljoin(page.url, page_form_action)
        print(url_to_post)

        post_result = session_request.post(url_to_post, headers=headers, data=data_to_send)
        print('trying to investigate the request...')
        # print(post_result.request.headers)
        print(post_result.text)
        print(post_result.status_code)
        json_object = json.loads(post_result.text)
        gdfiles_url = json_object['url']
        print('printing the url found')
        print(gdfiles_url)

        return [{'name': gdfiles_url,
                                  'thumb': '',
                                  'video': gdfiles_url,
                                  'genre': ''}]
