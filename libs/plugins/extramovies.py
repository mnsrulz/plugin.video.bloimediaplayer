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


class ExtraMovies(BaseClassPlugin):
    name = "hdhub4u"
    domains = ['hdhub4u']
    pattern = r'(?://|\.)(extramovies\.best)'

    def get_content(self, content_url):
        print('inside extramovies dynamic module')
        if not re.match('https?:\/\/extralinks.[\w\d]*/view', content_url) and \
                (content_url.startswith('https://extramovies') or content_url.startswith('http://extramovies')):
            return self.execute(content_url)
        else:
            return False

    def execute(self, content_url):
        genre = 'movie'
        movieList = []
        print('downloading extramovies content url: ' + content_url)
        page = requests.get(content_url)
        print(page.status_code)
        main_page = common.parseDOM(page.text, 'div', attrs={"class": "entry clearfix"})
        if len(main_page) == 0:
            main_page = common.parseDOM(page.text, 'div', attrs={"class": "wrap"})
        found_link = False
        print('found extra movies content....')
        print(len(main_page))
        if len(main_page) > 0:
            all_links = common.parseDOM(main_page, 'a')
            all_links_titles = common.parseDOM(main_page, 'a', ret='href')
            thumb = next(iter(common.parseDOM(main_page, 'img', ret='src')), '')

            # for row in all_links:
            for i in range(0, len(all_links)):
                video_link = all_links_titles[i]
                print('Printing original video link : ' + video_link)
                video_link = urljoin(page.url, video_link)
                absolute_parsed_url = urlparse(video_link)
                row = all_links[i]
                if absolute_parsed_url.path.startswith('/drive.php'):
                    print('found a google drive link... downloading the content of the page')
                    parsed_base_url = urlparse(content_url)
                    google_drive_download_page = requests.get(video_link)
                    google_drive_links = common.parseDOM(google_drive_download_page.text, 'a', ret='href')
                    for each_link in google_drive_links:
                        if each_link.startswith('http://extralinks'):
                            video_link = each_link
                elif absolute_parsed_url.path.startswith('/download.php'):
                    video_link = video_link.replace('#038;', '')    # cleaning a bit
                    print('printing query segments of the url')
                    query_param = parse_qs(urlparse(video_link).query)
                    print(parse_qs(urlparse(video_link).query))
                    decoded_link = base64.b64decode(query_param['link'][0])
                    print('decoded link : ' + decoded_link)
                    video_link = decoded_link
                elif absolute_parsed_url.path.startswith('/vidoza.php'):
                    query_param = parse_qs(absolute_parsed_url.query)
                    decoded_link = query_param['url'][0]
                    video_link = 'https://vidoza.net/' + decoded_link
                    print('vidoza link found... ' + video_link)
                elif absolute_parsed_url.path.startswith('/uptostream.php'):
                    query_param = parse_qs(absolute_parsed_url.query)
                    decoded_link = query_param['url'][0]
                    video_link = 'https://uptostream.com/' + decoded_link
                    print('uptostream link found... ' + video_link)
                elif re.match('\/(trailer.php|cast\/|director\/|author\/)', absolute_parsed_url.path) or \
                        absolute_parsed_url.netloc.startswith('ghoto-12'):
                    print('Ignoring this link')
                    continue
                elif 'extralinks' in video_link:
                    print('found a extralink...')
                else:
                    video_link = absolute_parsed_url.geturl()
                    print('some unknown link... still adding')
                    #continue

                print('printing all_links element second time')
                # if row.startswith('https://linkstaker.') or row.startswith('https://linkscare.net'):
                print('found one useful link: ' + video_link)
                # print(row)
                found_link = True
                movieList.append({'name': common.stripTags(row) + ' ## ' + video_link,
                                  'thumb': thumb,
                                  'video': video_link,
                                  'genre': genre}
                                 )

        if not found_link:
            filepath = os.path.join(xbmc.translatePath('special://home'), 'userdata', 'extramovies.json')
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
            dp.create("Extramovies", "", content_url)
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
                upper = common.parseDOM(page.text, 'div', attrs={'class': 'imag'})
                print(upper)
                # soup = BeautifulSoup(page.text, 'html.parser')
                # upper = soup.find_all('div', attrs={'class': 'bw_thumb_title'})
                for row in upper:
                    # print(row)
                    thumb = common.parseDOM(row, 'img', ret='src')[0]
                    # print(thumb)
                    figure_caption = common.parseDOM(row, 'a', ret='title')[0]
                    # print(figure_caption)
                    title = common.stripTags(figure_caption)
                    # print(title)
                    video_url = common.parseDOM(row, 'a', ret='href')[0]
                    # print(video_url)

                    if video_url in all_urls:
                        looper = False
                        continue

                    new_listings_added = True

                    new_movieList.append({
                        'video': video_url,
                        'thumb': thumb,
                        'name': title,
                        'genre': genre
                    })

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
