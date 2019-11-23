import re
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


class GoMovies(BaseClassPlugin):
    name = "GoMovies"
    domains = ['GoMovies']
    pattern = r'(?://|\.)(GoMovies\.best)'

    def get_content(self, content_url):
        print('inside GoMovies dynamic module')
        if content_url.startswith('https://ww1.0gomovies.com'):
            return self.execute(content_url)
        else:
            return False


    def execute(self, content_url):
        genre = 'movie'
        movieList = []
        print('downloading gomovies content url')
        print(content_url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
            'Referer': 'https://ww1.0gomovies.com/browse/'
        }
        page = requests.get(content_url, verify=False)
        print(page.status_code)
        main_page = common.parseDOM(page.text, 'div', attrs={"class": "page-detail"})
        found_link = False
        print('found content....')
        print(len(main_page))
        if len(main_page) > 0:
            watch_link = common.parseDOM(page.text, 'a', attrs={"class": "bwac-btn"}, ret='href')[0]
            print('printing watch link')
            print(watch_link)

            inner_page_content = requests.get(watch_link, verify=False)
            server_url_container = common.parseDOM(inner_page_content.text, 'div', attrs={"class": "pas-list"})[0]
            print('printing episode first element')
            print(server_url_container)

            all_link_text = re.findall('http[^"]*', server_url_container)

            for i in all_link_text:
                row_link = i
                row_title = i
                print('printing all_links element second time')
                found_link = True
                movieList.append({'name': row_title,
                                  'thumb': '',
                                  'video': row_link,
                                  'genre': genre}
                                 )

        if not found_link:
            filepath = os.path.join(xbmc.translatePath('special://home'), 'userdata', 'gomovies.json')
            all_urls = []
            new_listings_added = False
            looper = True
            new_movieList = []
            page_counter = 0
            if os.path.isfile(filepath):
                with open(filepath) as f:
                    movieList = json.load(f)
                    for m in movieList:
                        all_urls.append(m['video'])
            dp = xbmcgui.DialogProgress()
            dp.create("GoMovies", "", content_url)
            total_pages = 0
            try:
                last_page = 277  # common.parseDOM(page.text, 'a', attrs={'class': 'pagination'})[-1]
                # last_page = common.stripTags(last_page)
                # last_page = last_page.replace('Page', '')
                total_pages = int(last_page)
            except ValueError:
                total_pages = 1000  # consider max 1000 pages

            while looper:
                if dp.iscanceled():
                    return new_movieList + movieList

                page_counter = page_counter + 1
                percent = min((page_counter * 100) / total_pages, 100)
                dp.update(percent, "Fetching page %s" % content_url, "%s of %s" % (page_counter, total_pages))

                page = requests.get(content_url, verify=False)
                upper = common.parseDOM(page.text, 'div', attrs={'class': 'ml-item'})
                for row in upper:
                    thumb = common.parseDOM(row, 'img', ret='src')[0]
                    figure_caption = common.parseDOM(row, 'span', attrs={'class': 'mli-info'})[0]
                    title = common.stripTags(figure_caption)
                    video_url = common.parseDOM(row, 'a', ret='href')[0]
                    if video_url in all_urls:
                        looper = False
                        continue

                    new_listings_added = True

                    new_movieList.append({'name': title,
                                          'thumb': thumb,
                                          'video': video_url,
                                          'genre': genre}
                                         )
                pagination_container = common.parseDOM(page.text, 'ul', attrs={'class': 'pagination'})
                last_link = common.parseDOM(pagination_container, 'a', ret='href')[-2]
                print(last_link)
                last_link_text = common.parseDOM(pagination_container, 'a')[-2]
                print(last_link_text)
                if common.stripTags(last_link_text).startswith('Next'):
                    print('going to iterate next....')
                    content_url = last_link
                else:
                    looper = False
            if new_listings_added:
                with open(filepath, 'w') as outfile:
                    movieList = new_movieList + movieList
                    json.dump(movieList, outfile)

        return movieList
