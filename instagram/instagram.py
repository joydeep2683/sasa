import json
import requests
import math
from threading import Lock
import random


class Instagram():

    def __init__(self):
        pass

    def get_hashtags_from_keyword(self, trend_name):
        keyword = trend_name.replace('-', '').replace('_', '').replace(' ', '').replace('&', '').lower()
        return keyword

    def get_id_from_user_name(self, user_name):
        url = 'https://www.instagram.com/{}/?__a=1'.format(user_name)
        R = requests.get(url)
        user_id = R.json()['graphql']['user']['id']
        return user_id

    def return_clean_data(self, raw):
        edges = raw['edges']
        cleaned_data = []
        for edge in edges:
            post_id = edge['node']['shortcode']
            taken_at_time = edge['node']['taken_at_timestamp']
            comment_count = edge['node']['edge_media_to_comment']['count']
            display_url = edge['node']['display_url']
            like_count = edge['node']['edge_media_preview_like']['count']
            text_content = edge['node']['edge_media_to_caption']['edges'][0]['node']['text']
            xc = {'post_id': post_id, 'taken_at_time': taken_at_time, 'comment_count': comment_count, 'like_count': like_count, 'text_content': text_content, 'display_url': display_url}
            cleaned_data.append(xc)
        return cleaned_data


    def get_data_for_user(self, user_name, no_of_post=50):
        #working code, test with '_karasky_8' id
        user_id = self.get_id_from_user_name(user_name)
        data = []
        if no_of_post > 50:
            url = 'https://www.instagram.com/graphql/query/?query_id=17888483320059182&id={}&first={}'.format(user_id, no_of_post)
            R = requests.get(url)
            raw = R.json()['data']['user']['edge_owner_to_timeline_media']
            has_next_page = raw['page_info']['has_next_page']
            dt = self.return_clean_data(raw)
            data.append(dt)
            total_post_count = raw['count']
            if has_next_page:
                end_cursor = raw['page_info']['end_cursor']
                check = math.ceil(no_of_post/50)-1
                for i in range(0, math.ceil(no_of_post/50)-1):
                    if i == check-1:
                        post = no_of_post%50
                        if no_of_post%50 == 0:
                            post = 50
                    else:
                        post = 50
                    url = 'https://www.instagram.com/graphql/query/?query_id=17888483320059182&id={}&first={}&after={}'.format(user_id, post, end_cursor)
                    R = requests.get(url)
                    raw = R.json()['data']['user']['edge_owner_to_timeline_media']
                    has_next_page = raw['page_info']['has_next_page']
                    end_cursor = raw['page_info']['end_cursor']
                    dt = self.return_clean_data(raw)
                    data.append(dt)
        else:    
            url = 'https://www.instagram.com/graphql/query/?query_id=17888483320059182&id={}&first={}'.format(user_id, no_of_post)
            R = requests.get(url)
            raw = R.json()['data']['user']['edge_owner_to_timeline_media']
            total_post_count = raw['count']
            dt = self.return_clean_data(raw)
            data.append(dt)
        foo = {'name': user_name, 'source': 'instagram_user', 'data': data, 'total_post_count': total_post_count}
        return foo


    def fetch_hashtag_count(self, tag):
        keyword = tag.lower().replace(' ', '').replace('-', '').replace('&', '')
        url = 'https://www.instagram.com/explore/tags/{}/?__a=1'.format(keyword)
        r = requests.get(url)
        time.sleep(2)
        data = {}
        data['trend_name'] = tag
        data['source'] = 'instagram'
        try:
            data['hashtagcount'] = json.loads(r.text)['graphql']['hashtag']['edge_hashtag_to_media']['count']
        except:
            data['hashtagcount'] = 0
        return data