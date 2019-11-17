import sys
from urllib import urlencode
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


class TamilMV(BaseClassPlugin):
    name = "TamilMV"
    domains = ['TamilMV']
    pattern = r'(?://|\.)(TamilMV\.best)'

    def get_content(self, content_url):
        print('inside TamilMV dynamic module')
        if content_url.startswith('https://www.tamilmv'):
            return self.execute(content_url)
        else:
            return False


    def execute(self, content_url):
        movieList = []
        genre = 'movie'
        headers = {
            'User-Agent': 'Mozilla'
        }
        page = requests.get(content_url, headers=headers)
        # print(page)
        print(content_url)
        print(page.status_code)
        print('getting pln container')
        pln_container = common.parseDOM(page.text, 'span', attrs={'class': 'pln'})
        print(len(pln_container))

        if len(pln_container) > 0:
            all_links = pln_container[0].splitlines()
            for row in all_links:
                print(row)
                movieList.append({'name': row,
                                  'thumb': '',
                                  'video': row,
                                  'genre': genre}
                                 )
            print(all_links)
        else:
            upper_container = common.parseDOM(page.text, 'div', attrs={'class': 'ipsWidget_inner '})
            print(len(upper_container))
            upper = common.parseDOM(upper_container, 'a', ret='href')
            print(upper[0])
            # soup = BeautifulSoup(page.text, 'html.parser')
            # upper = soup.find_all('div', attrs={'class': 'bw_thumb_title'})
            print('iterating the thumb titles')
            print(len(upper))
            print(upper)
            for row in upper:
                print(row)
                thumb = ''  # common.parseDOM(row, 'img', ret='src')[0]
                # print(thumb)
                title = row
                if title.endswith('/'):
                    title = title[:-1]

                title = title.rsplit('/', 1)[-1]
                # print(title)
                video_url = row

                movieList.append({'name': title,
                                  'thumb': thumb,
                                  'video': video_url,
                                  'genre': genre}
                                 )
        return movieList

