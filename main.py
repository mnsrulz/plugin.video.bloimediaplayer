# -*- coding: utf-8 -*-
# Module: default
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urllib import urlencode
from urlparse import urljoin
from urlparse import parse_qsl
from urlparse import urlparse, parse_qs
import xbmc
import xbmcgui
import xbmcplugin
import requests
import re
import json
import CommonFunctions
import time
import base64
import HTMLParser
import os
import urlresolver
from libs.bcp import BaseClassPlugin
from libs.plugins import *

common = CommonFunctions
# from bs4 import BeautifulSoup

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

# Free sample videos are provided by www.vidsplay.com
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.
VIDEOS = {'https://www.tamilmv.cz': [{'name': 'Chicken',
                    'thumb': 'https://www.tamilmv.cz/uploads/monthly_2018_02/logo.png.635a011b01c97555a09f57bfd0e6b405.png.7eb11ef9469043049d2a5ab0b57d468f.png',
                    'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/bbqchicken.mp4',
                    'genre': 'Food'}],
          'https://movieretina.in': [{'name': 'Chicken',
                    'thumb': 'https://2.bp.blogspot.com/-u8ya2x-bSTs/W4765dKMORI/AAAAAAAAAtI/-x5_yrgo3Bk8iylKMoeRg7Qtm4Xck2TBQCLcBGAs/s1600/MovieRetina%2BBlue%2BLogo.png',
                    'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/bbqchicken.mp4',
                    'genre': 'Food'}],
          'https://extramovies.blue': [{'name': 'Chicken',
                    'thumb': 'https://extramovies.blue/wp-content/uploads/2018/03/logo.png',
                    'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/bbqchicken.mp4',
                    'genre': 'Food'}],
          'https://hdhub4u.host': [{'name': 'Chicken',
                    'thumb': 'https://hdhub4u.pw/wp-content/uploads/2018/09/rsz_1coollogo_com-16691619.png',
                    'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/bbqchicken.mp4',
                    'genre': 'Food'}]}


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def is_playable(content_url):
    print('is playable called for ')
    print(content_url)
    if content_url.startswith('https://linkstaker.') or content_url.startswith('https://mvlinks.ooo') \
            or content_url.startswith('https://anotepad') \
            or content_url.startswith('https://pastebin') \
            or content_url.startswith('https://vidoza') \
            or re.match('https:\/\/(zupload|userscloud|streamango|streamcherry|'
                        'clicknupload|racaty|desiupload|bdupload|www.indishare|indishare)', content_url) \
            or re.match('https:\/\/(drive|docs).google.com', content_url) \
            or content_url.startswith('https://openload') \
            or re.match('https?:\/\/extralinks.[\w\d]*/more', content_url) \
            or content_url.startswith('http://filecupid') or content_url.startswith('https://filecupid'):
        return True
    elif is_uptostream_domain(content_url):
        return True
    else:
        return False


def is_uptostream_domain(content_url):
    return urlparse(content_url).netloc.endswith('uptostream.com')


def get_categories():
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: types.GeneratorType
    """
    return VIDEOS.iterkeys()


def get_folder_content(category):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or server.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """
    print('We are in get_category folder: ' + category)

    return_value = dynamic_execute(category)
    if return_value:
        return return_value

    if category.startswith('https://solarsystem')\
            or category.startswith('https://cr-news'):
        # Play a video from a provided URL.
        return get_solarsystem(category)
    elif category.startswith('https://hblinks.pw'):
        return get_generic(category)
    elif category.startswith('https://linkscare') or category.startswith('https://linkrit')\
            or category.startswith('https://keeplinks')\
            or re.match('https?:\/\/extralinks.[\w\d]*/view', category):
        return get_linkscare(category)
    elif category.startswith('https://uptobox.com'):
        return uptoboxRESOLVER(category)
    else:
        return VIDEOS[category]


def load_modules():
    print('calling load modules')
    classes = BaseClassPlugin.__class__.__subclasses__(BaseClassPlugin)
    print('printing all the classes')
    print(classes)

    for c in classes:
        print(c)
        ob = c()
        print('object created dynamically')
        yield ob


def dynamic_execute(cu):
    for inst in load_modules():
        return_value = inst.get_content(cu)
        if return_value:
            return return_value
    return False


def get_linkscare(content_url):
    movieList = []
    headers = {
        'User-Agent': 'Mozilla'
    }
    sessionrequest = requests.session()
    page = sessionrequest.get(content_url, headers=headers)
    print('fetching links care url')
    print(content_url)
    print(page.status_code)
    csrf_token_name = common.parseDOM(page.text, 'input', attrs={'type': 'hidden'}, ret='name')[0]
    csrf_token_value = common.parseDOM(page.text, 'input', attrs={'type': 'hidden'}, ret='value')[0]
    payload = {csrf_token_name: csrf_token_value}
    print('post payload ready to post')
    print(payload)
    post_result = sessionrequest.post(page.url, data=payload, headers=headers)
    print(post_result.status_code)
    # print(post_result.text.encode('ascii', 'ignore').decode('ascii'))
    container_div = \
    common.parseDOM(post_result.text, 'div', attrs={'class': 'col-sm-8 col-sm-offset-2 well view-well'})
    if len(container_div) > 0:
        upper = common.parseDOM(container_div[0], 'a', ret='href')
    else:
        upper = common.parseDOM(post_result.text, 'a', ret='href')
    print(upper)
    for row in upper:
        video_url = row
        genre = 'movie'
        thumb = 'https://www.jiopic.com/images/2018/11/16/vlcsnap-2018-11-16-00h23m58s651.png'  # sample only
        print(video_url)
        movieList.append({'name': video_url,
                          'thumb': thumb,
                          'video': video_url,
                          'genre': genre}
                         )
    return movieList


def get_solarsystem(content_url):
    movieList = []
    print('fetching solarsystem url')
    print(content_url)
    page = requests.get(content_url)
    print(page.status_code)

    safeLinkContainer = common.parseDOM(page.text, 'div', attrs={'id': 'wpsafe-link'})

    j = common.parseDOM(safeLinkContainer, "a", ret="href")

    for row in j:
        # row = urlparse(row)
        query_param = parse_qs(urlparse(row).query)
        video_url = query_param['safelink_redirect'][0]
        genre = 'movie'
        print(video_url)
        movieList.append({'name': video_url,
                          'thumb': "",
                          'video': video_url,
                          'genre': genre}
                         )
    return movieList


def get_generic(content_url):
    movieList = []
    print('fetching generic url')
    print(content_url)
    page = requests.get(content_url)
    print(page.status_code)

    j = common.parseDOM(page.text, "a", ret="href")

    for row in j:
        video_url = row
        genre = 'movie'
        print(video_url)
        movieList.append({'name': video_url,
                          'thumb': "",
                          'video': video_url,
                          'genre': genre}
                         )
    return movieList


def uptobox(content_url):
    content_url = content_url.replace('uptobox.com', 'uptostream.com')
    movieList = []
    print('fetching uptobox/uptostream url')
    print(content_url)
    page = requests.get(content_url)
    print(page.status_code)

    result = re.findall('poster.*,', page.text)[0]
    print('regex 1 found match')
    print(result)
    thumb = result.split("'")[1]

    result2 = re.findall('window\.sources.*;', page.text)[0]
    print('regex 2 found match')
    print(result2)
    json_urls = result2.split("'")[1]

    j = json.loads(json_urls)

    for row in j:
        video_url = row['src']
        genre = 'movie'
        print(video_url)
        movieList.append({'name': video_url,
                          'thumb': thumb,
                          'video': video_url,
                          'genre': genre}
                         )
    return movieList


def uptoboxRESOLVER(content_url):
    video_url = urlresolver.resolve(content_url)
    movieList = []
    genre = 'movie'
    print(video_url)
    movieList.append({'name': video_url,
                      'thumb': '',
                      'video': video_url,
                      'genre': genre}
                     )
    return movieList


def get_mvlinks_playable_path(content_url):
    print('fetching mvlinks url: ' + content_url)
    # print(content_url)
    headers = {
        'User-Agent': 'Mozilla'
    }
    page = requests.get(content_url, headers=headers)
    print(page.status_code)
    # print(page.text)

    index = 0

    urlsresults = re.findall("https?:\/\/urls.[^\s\"'<]*", page.text)
    print('printing list of playable mvlinks urls')
    print(urlsresults)
    if len(urlsresults) > 1:
        urlsresults = list(set(urlsresults))
        # Noticed that two links are there now, so letting the user select the server
        links = list(map(lambda x: "Link# " + str(x+1), range(len(urlsresults))))
        index = xbmcgui.Dialog().select(heading='Multiple links found - Choose one link',
                                        list=['Choose server '] + links)
        # index = xbmcgui.Dialog().select(heading='Choose Server',
        #                                list=['Server 1 (Private)', 'Server 2 (Google)'])
        # index = index - 1

    print('Index selected: ' + str(index))
    if index < 1:
        return ""
    result = urlsresults[index - 2]

    # result = result[:-1]
    print('found elinks for the mvlink content')
    print(result)
    elinks_requests = requests.session()
    elinks_page = elinks_requests.get(result, headers=headers)
    print('getting the result for :' + result)

    if elinks_page.status_code != 200:  # if status code not equals to 200 return from here
        print('url status code return non 200 status code')
        return ""
    print(elinks_page.status_code)
    print(elinks_page.headers)
    name_collection = common.parseDOM(elinks_page.text, 'input', ret='name')
    value_collection = common.parseDOM(elinks_page.text, 'input', ret='value')
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
    time.sleep(16)  # Waiting for 16 seconds
    post_result = elinks_requests.post('https://urls.work/links/go', headers=headers, data=data_to_send)
    print('trying to investigate the request...')
    # print(post_result.request.headers)
    print(post_result.text)
    print(post_result.status_code)
    json_object = json.loads(post_result.text)
    gdfiles_url = json_object['url']

    headers = {
        'User-Agent': 'Mozilla',
        'referer': result
    }
    gdfiles_url_result = requests.get(gdfiles_url, headers=headers)
    print('gdfiles_url processing completed with status code')
    print(gdfiles_url_result.status_code)
    print(gdfiles_url_result.headers)
    refresh_header_value = gdfiles_url_result.headers['refresh']
    refresh_header_url_value = re.findall('https.*', refresh_header_value)[0]
    return refresh_header_url_value


def get_gdrive_playable_path(content_url):
    gdrive_request = requests.session()
    r = gdrive_request.get(content_url, allow_redirects=False)
    print(content_url)
    print(r.status_code)
    if r.status_code == 302:
        redirect_location = r.headers['Location']
        if urlparse(redirect_location).netloc.endswith('googleusercontent.com'):
            return redirect_location
        else:
            return ''
    elif r.status_code == 200:
        h = HTMLParser.HTMLParser()
        download_link = 'https://' + urlparse(content_url).netloc \
                        + h.unescape(common.parseDOM(r.text, "a", attrs={"id": "uc-download-link"}, ret="href")[0])
        print(download_link)
        r = gdrive_request.get(download_link, allow_redirects=False)
        print(r.status_code)
        return r.headers['Location']
    else:
        return ''


def get_zupload_playable_path(content_url):
    print('fetching zupload url: ' + content_url)
    zuploadsessionrequest = requests.session()
    page = zuploadsessionrequest.get(content_url)
    print(page.status_code)
    pt_value = common.parseDOM(page.text, 'input', attrs={'name': 'pt'}, ret='value')[0]
    payload = {
                'pt': pt_value,
                'user_name': '',
                'submit': 'Submit'
                }
    print('post data... ')
    print(payload)
    post_result = zuploadsessionrequest.post(page.url, data=payload)
    print(post_result.status_code)
    print(post_result.text)
    download_link = common.parseDOM(post_result.text, 'a', attrs={'class': 'link_button'}, ret='href')[0]
    return download_link


def get_userscloud_playable_path(content_url):
    print('fetching userscloud url: ' + content_url)
    userscloudsessionrequest = requests.session()
    page = userscloudsessionrequest.get(content_url)
    print(page.status_code)
    form_which_need_to_post = common.parseDOM(page.text, 'Form', attrs={'name': 'F1'})[0]
    print(form_which_need_to_post)
    name_collection = common.parseDOM(form_which_need_to_post, 'input', ret='name')
    value_collection = common.parseDOM(form_which_need_to_post, 'input', ret='value')
    payload = {}
    for n, v in zip(name_collection, value_collection):
        payload[str(n)] = str(v)
    print('post payload ready to post')
    print(payload)
    post_result = userscloudsessionrequest.post(page.url, data=payload)
    print(post_result.status_code)
    print('printing entire page another time')
    print(post_result.text)
    download_links = common.parseDOM(post_result.text, 'a', ret='href')
    for download_link in download_links:
        print(download_link)
        if 'usercdn' in download_link:
            return download_link
    return ''


def get_clicknupload_playable_path(content_url):
    print('fetching clicknupload url: ' + content_url)
    clicknuploadsessionrequest = requests.session()
    page = clicknuploadsessionrequest.get(content_url)
    print(page.status_code)
    form_which_need_to_post = common.parseDOM(page.text, 'Form')[0]
    print(form_which_need_to_post)
    id_value = common.parseDOM(form_which_need_to_post, 'input', attrs={'name': 'id', 'type': 'hidden'}, ret='value')[0]
    payload = {}
    payload['op'] = 'download2'
    payload['id'] = id_value
    payload['rand'] = ''
    payload['referer'] = page.url
    payload['method_free'] = 'Free Download >>'
    payload['method_premium'] = ''
    payload['adblock_detected'] = ''

    # for n, v in zip(name_collection, value_collection):
    #     payload[str(n)] = str(v)
    print('post payload ready to post')
    print(payload)
    post_result = clicknuploadsessionrequest.post(page.url, data=payload)
    print(post_result.status_code)
    # print('printing clicknupload page post form')
    # print_normalized(post_result.text)

    download_links = common.parseDOM(post_result.text, 'button', attrs={'id': 'downloadbtn'}, ret='onClick')[0]
    final_download_url = re.findall("http[^']*", download_links)[0]
    print('found some useful for clicknupload')
    print_normalized(final_download_url)
    return final_download_url


def get_racaty_playable_path(content_url):
    print('fetching racaty url: ' + content_url)
    racatysessionrequest = requests.session()
    page = racatysessionrequest.get(content_url)
    print(page.status_code)
    form_which_need_to_post = common.parseDOM(page.text, 'form')[0]
    print(form_which_need_to_post)
    id_value = common.parseDOM(form_which_need_to_post, 'input', attrs={'name': 'id', 'type': 'hidden'}, ret='value')[0]
    token_value = common.parseDOM(form_which_need_to_post, 'input', attrs={'name': 'token', 'type': 'hidden'}, ret='value')[0]
    fname_value = common.parseDOM(form_which_need_to_post, 'input', attrs={'name': 'fname', 'type': 'hidden'}, ret='value')[0]
    payload = {}
    payload['op'] = 'download2'
    payload['id'] = id_value
    payload['usr_login'] = ''
    payload['referer'] = page.url
    payload['token'] = token_value
    payload['method_free'] = 'Free Download'
    payload['fname'] = fname_value

    print('post payload ready to post')
    print(payload)
    post_result = racatysessionrequest.post(page.url, allow_redirects=False, data=payload)
    print(post_result.status_code)
    return post_result.headers['Location']


def get_desiupload_playable_path(content_url):
    print('fetching desiupload/indishare url: ' + content_url)
    desiuploadsessionrequest = requests.session()
    page = desiuploadsessionrequest.get(content_url)
    print(page.status_code)
    form_which_need_to_post = common.parseDOM(page.text, 'form', attrs={'name': 'F1'})[0]
    print(form_which_need_to_post)
    id_value = common.parseDOM(form_which_need_to_post, 'input', attrs={'name': 'id', 'type': 'hidden'}, ret='value')[0]
    payload = {}
    payload['op'] = 'download2'
    payload['id'] = id_value

    print('post payload ready to post')
    print(payload)
    post_result = desiuploadsessionrequest.post(page.url, data=payload)
    print(post_result.status_code)
    download_span_container = common.parseDOM(post_result.text, 'span', attrs={'id': 'direct_link'})
    final_download_url = common.parseDOM(download_span_container, 'a', ret='href')[0]
    print(final_download_url)
    return final_download_url


def get_bdupload_playable_path(content_url):
    print('fetching bdupload url: ' + content_url)
    bduploadsessionrequest = requests.session()
    page = bduploadsessionrequest.get(content_url)
    print(page.status_code)
    form_which_need_to_post = common.parseDOM(page.text, 'form', attrs={'name': 'F1'})[0]
    print(form_which_need_to_post)
    id_value = common.parseDOM(form_which_need_to_post, 'input', attrs={'name': 'id', 'type': 'hidden'}, ret='value')[0]
    payload = {}
    payload['op'] = 'download2'
    payload['id'] = id_value

    print('post payload ready to post')
    print(payload)
    post_result = bduploadsessionrequest.post(page.url, data=payload)
    print(post_result.status_code)
    print_normalized(post_result.text)
    regexmatches = re.findall('http:\/\/\w*.indifiles.com[^"]*', post_result.text)
    return regexmatches[0]


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'My Video Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
                          'icon': VIDEOS[category][0]['thumb'],
                          'fanart': VIDEOS[category][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_contents(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.
    videos = get_folder_content(category)
    print('listing contents....')
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': unescape(video['name']),
                                    'genre': video['genre'],
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!

        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        # print('getting url of the video link')
        # print(video['video'])
        if is_playable(video['video']):
            list_item.setLabel(video['name'] + '[COLOR=yellow] ***SUPPORTED*** [/COLOR]')
            list_item.setProperty('IsPlayable', 'true')
            url = get_url(action='play', video=video['video'])
            is_folder = False
        else:
            url = get_url(action='listing', category=video['video'])
            is_folder = True
        # url = get_url(action='play', video=video['video'])
        # check via url whether this is a folder or playable url
        # url = video['video']
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    print('trying to find the playable source for : ' + path)
    # we need to make practice of using regex more & more
    resolvedpath = urlresolver.resolve(path)
    print(path)
    print('resolved url ')
    print(resolvedpath)

    if resolvedpath:
        path = resolvedpath
    elif re.match('https?:\/\/(linkstaker|extralinks)', path):
        page = requests.get(path)
        print('fetching links care url')
        print(path)
        print(page.status_code)
        result = re.findall('https.*e=download', page.text)[0]
        print('regex found match')
        print(result)
        path = result
    elif re.match('https?:\/\/(mvlinks|anotepad|pastebin)', path):
        path = get_mvlinks_playable_path(path)
    elif re.match('https:\/\/(drive|docs).google.com', path):
        path = get_gdrive_playable_path(path)
    elif path.startswith('http://filecupid.com') or path.startswith('https://filecupid.com') or \
            path.startswith('https://vidoza.net') or path.startswith('http://vidoza.net'):
        page = requests.get(path)
        path = common.parseDOM(page.text, 'source', ret='src')[0]
    elif re.match('https?:\/\/zupload', path):
        path = get_zupload_playable_path(path)
    elif re.match('https?:\/\/userscloud', path):
        #path = get_userscloud_playable_path(path)
        path = urlresolver.resolve(path)
    elif re.match('https?:\/\/clicknupload', path):
        path = get_clicknupload_playable_path(path)
    elif re.match('https?:\/\/racaty', path):
        path = get_racaty_playable_path(path)
    elif re.match('https?:\/\/desiupload', path) or re.match('https?:\/\/www.indishare', path):
        path = get_desiupload_playable_path(path)
    elif re.match('https?:\/\/bdupload', path):
        path = get_bdupload_playable_path(path)
    elif re.match('https?:\/\/(streamango|streamcherry|openload)', path):
        page = requests.get(path)
        result = requests.post('https://gd2gp-dev.herokuapp.com/ol', json={'b': page.text, 'u': path})
        print(result.status_code)
        print(result.text)
        json_response = json.loads(result.text)
        path = json_response[0]['src']
    if not path:
        print('Nothing to play')
    else:
        # Create a playable item with a path to play.
        play_item = xbmcgui.ListItem(path=path)
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def print_normalized(content):
    print(content.encode('ascii', 'ignore').decode('ascii'))


def unescape(content):
    h = HTMLParser.HTMLParser()
    return h.unescape(content)


def clear_cache(provider):
    filepath = ''
    if provider == 'Extramovies':
        filepath = os.path.join(xbmc.translatePath('special://home'), 'userdata', 'extramovies.json')
        print('clearning extramovies cache')
    elif provider == 'HdHub4u':
        filepath = os.path.join(xbmc.translatePath('special://home'), 'userdata', 'hdhub.json')
    elif provider == 'MovieRetina':
        filepath = os.path.join(xbmc.translatePath('special://home'), 'userdata', 'movieretina.json')
    else:
        print('Unable to clear cache. Error: Invalid provider')
        return
    with open(filepath, 'w') as outfile:
        movieList = []
        json.dump(movieList, outfile)
        xbmc.executebuiltin(
            'Notification(Cache cleared successfully,5000)')


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_contents(params['category'])
        elif params['action'] == '_clear_cache':
            # Play a video from a provided URL.
            clear_cache(params['provider'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
