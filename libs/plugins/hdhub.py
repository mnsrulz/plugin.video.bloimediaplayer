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


class HdHub(BaseClassPlugin):
    name = "hdhub4u"
    domains = ['hdhub4u']
    pattern = r'(?://|\.)(hdhub4u\.best)'

    def get_content(self, content_url):
        print('inside hdhub4u dynamic module')
        if content_url.startswith('https://hdhub4u'):
            return self.execute(content_url)
        else:
            return False


    def execute(self, content_url):
        genre = 'movie'
        movieList = []
        print('downloading hdhub content url')
        # print(content_url)
        page = requests.get(content_url)
        print(page.status_code)
        main_page = common.parseDOM(page.text, 'main', attrs={"class": "page-body"})
        found_link = False
        print('found content....')
        print(len(main_page))
        if len(main_page) > 0:
            all_links = common.parseDOM(main_page[0], 'a', ret='href')
            all_link_text = common.parseDOM(main_page[0], 'a')
            thumb = common.parseDOM(main_page[0], 'img', ret='src')[0]  # sample only

            for i in range(0, len(all_links)):
                row_link = all_links[i]
                row_title = common.stripTags(all_link_text[i]) + " #(" + row_link + ")"

                # print(thumb)
                # figure_caption = common.parseDOM(row, 'figcaption')[0]
                print('printing all_links element second time')
                # if row.startswith('https://linkstaker.') or row.startswith('https://linkscare.net'):
                # print('found one useful link')
                # print(row)
                found_link = True
                movieList.append({'name': row_title,
                                  'thumb': thumb,
                                  'video': row_link,
                                  'genre': genre}
                                 )
                # group = {}
                # group['contact'] = ids[i]
                # group['Title'] = titles[i]

            # for row in all_links:
            #     row_href = common.parseDOM(row, ret='href')[0]
            #     row_href = common.parseDOM(row, ret='href')[0]
            #     # print(thumb)
            #     figure_caption = common.parseDOM(row, 'figcaption')[0]
            #     print('printing all_links element second time')
            #     # if row.startswith('https://linkstaker.') or row.startswith('https://linkscare.net'):
            #     print('found one useful link')
            #     print(row)
            #     found_link = True
            #     movieList.append({'name': row_title,
            #                       'thumb': thumb,
            #                       'video': row,
            #                       'genre': genre}
            #                      )
        if not found_link:
            filepath = os.path.join(xbmc.translatePath('special://home'), 'userdata', 'hdhub.json')
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
            dp.create("Hdhub4u", "", content_url)
            total_pages = 0
            try:
                last_page = common.parseDOM(page.text, 'a', attrs={'class': 'page-numbers'})[-1]
                last_page = common.stripTags(last_page)
                last_page = last_page.replace('Page', '')
                total_pages = int(last_page)
            except ValueError:
                total_pages = 1000  # consider max 1000 pages

            while looper:
                if dp.iscanceled():
                    return new_movieList + movieList

                page_counter = page_counter + 1
                percent = min((page_counter * 100) / total_pages, 100)
                dp.update(percent, "Fetching page %s" % content_url, "%s of %s" % (page_counter, total_pages))

                page = requests.get(content_url)
                upper = common.parseDOM(page.text, 'figure')
                print(upper)
                # soup = BeautifulSoup(page.text, 'html.parser')
                # upper = soup.find_all('div', attrs={'class': 'bw_thumb_title'})
                for row in upper:
                    # print(row)
                    thumb = common.parseDOM(row, 'img', ret='src')[0]
                    # print(thumb)
                    figure_caption = common.parseDOM(row, 'figcaption')[0]
                    # print(figure_caption)
                    title = common.stripTags(figure_caption)
                    # print(title)
                    video_url = common.parseDOM(figure_caption, 'a', ret='href')[0]
                    # print(video_url)
                    if video_url in all_urls:
                        looper = False
                        continue

                    new_listings_added = True

                    new_movieList.append({'name': title,
                                      'thumb': thumb,
                                      'video': video_url,
                                      'genre': genre}
                                     )
                next_page_link = common.parseDOM(page.text, 'a', attrs={'class': 'next page-numbers'}, ret='href')
                if len(next_page_link) > 0:
                    content_url = next_page_link[0]
                else:
                    looper = False
            if new_listings_added:
                with open(filepath, 'w') as outfile:
                    movieList = new_movieList + movieList
                    json.dump(movieList, outfile)

        return movieList

