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


class MovieRetina(BaseClassPlugin):
    name = "movieretina"
    domains = ['movieretina']
    pattern = r'(?://|\.)(movieretina\.best)'

    def get_content(self, content_url):
        print('inside movieretina dynamic module')
        if content_url.startswith('https://movieretina'):
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
        print("get movie retina: " + content_url)

        detail_page_container = common.parseDOM(page.text, 'div', attrs={'class': 'bw_desc'})

        if len(detail_page_container) > 0:
            found_link = False
            if "DelayRedirect()" in page.text:
                movie_title = common.stripTags(
                    common.parseDOM(page.text, 'h1', attrs={'class': 'bw_h1title_single'})[0])
                thumb = common.parseDOM(page.text, 'img', attrs={'class': 'bw_poster'}, ret='src')[0]
                print('Printing movie_retina page')
                print(re.findall('(?:anotepad|pastebin)[^"]*', page.text))
                print('new len of regex found: ' + str(len(re.findall('(?:anotepad|pastebin)[^"]*', page.text))))
                # print(page.text.encode('ascii', 'ignore').decode('ascii'))

                video_url = re.findall('(?:anotepad|pastebin)[^"]*', page.text)
                if len(video_url) > 0:
                    found_link = True
                    print('Found a movie_retina url: ' + 'https://' + video_url[0])
                    movieList.append({'name': movie_title,
                                      'thumb': thumb,
                                      'video': 'https://' + video_url[0],
                                      'genre': genre}
                                     )
            if not found_link:  # even if the link contains delayredirect text, some page still fails
                print('found detail page container')
                thumb = ''
                movie_thumb = common.parseDOM(detail_page_container, 'img', ret='src')
                if len(movie_thumb) > 0:
                    print('found detail page thumb')
                    thumb = movie_thumb[0]
                movie_links = common.parseDOM(detail_page_container, 'tr')
                for row in movie_links:
                    print('iterating movie links')
                    movie_links_title = common.parseDOM(row, 'th')
                    if len(movie_links_title) > 0:
                        print(movie_links_title)
                        movie_title = common.stripTags(movie_links_title[0])
                        print('movie link title found')
                        movie_links_details = common.parseDOM(row, 'td')
                        if len(movie_links_details) > 0:
                            print('movie link details found')
                            first_td = movie_links_details[0]
                            print(first_td)
                            regex_result = re.findall("https://mvlinks.*'", first_td)
                            if len(regex_result) > 0:
                                result = regex_result[0][:-1]
                                video_url = result
                                movieList.append({'name': movie_title,
                                                  'thumb': thumb,
                                                  'video': video_url,
                                                  'genre': genre}
                                                 )
        else:
            filepath = os.path.join(xbmc.translatePath('special://home'), 'userdata', 'movieretina.json')
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
            dp.create("MovieRetina", "", content_url)
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

                page = requests.get(content_url, headers=headers)
                upper = common.parseDOM(page.text, 'div', attrs={'class': 'bw_thumb_title'})
                # soup = BeautifulSoup(page.text, 'html.parser')
                # upper = soup.find_all('div', attrs={'class': 'bw_thumb_title'})
                print('iterating the thumb titles')
                print(upper)
                for row in upper:
                    thumb = common.parseDOM(row, 'img', ret='src')[0]
                    # print(thumb)
                    figure_caption = common.parseDOM(row, 'h1')[0]
                    # print(figure_caption)
                    title = common.stripTags(figure_caption)
                    # print(title)
                    video_url = common.parseDOM(row, 'a', ret='href')[0]
                    if video_url in all_urls:
                        looper = False
                        continue

                    new_listings_added = True

                    new_movieList.append({'name': title,
                                          'thumb': thumb,
                                          'video': video_url,
                                          'genre': genre})
                next_page_link = common.parseDOM(page.text, 'a', attrs={'class': 'next page-numbers'}, ret='href')
                print('printing the next page link')
                if len(next_page_link) > 0:
                    content_url = next_page_link[0]
                else:
                    looper = False
            if new_listings_added:
                with open(filepath, 'w') as outfile:
                    movieList = new_movieList + movieList
                    json.dump(movieList, outfile)
        return movieList