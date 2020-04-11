import math
import re

import vk_api


class VKGrabber:

    def __init__(self, login, password, key_words):
        self.__key_words = key_words
        self.__vk_session = vk_api.VkApi(login=login, password=password)
        self.__vk_session.auth()
        self.__vk = self.__vk_session.get_api()

    def __is_text_interesting(self, post):
        for key_word in self.__key_words:
            if re.search(key_word, post, flags = re.IGNORECASE):
                return True
        return False

    def is_group_exists(self, group):
        response = self.__vk.utils.resolveScreenName(screen_name=group)
        if len(response) == 0:
            return False
        else:
            return True if response['type'] == 'group' else False

    def get_interesting_posts_list(self, group):
        response = self.__vk.wall.get(domain=group, count=1)
        posts_count = response['count']
        request_count = math.ceil(posts_count / 2500)
        interesting_posts = []
        for i in range(request_count):
            response = self.__vk.execute(code='''
                var container = [];
                var offset = {0};
                var probe = API.wall.get({{domain:"{1}", count:100, filter:"all", offset:offset}});
                container.push(probe);
                offset = offset + 100;
                var iter;
                if (probe.count > 2400)
                    iter = 24;
                else
                    iter = probe.count / 100;
                while (iter > 0)
                {{
                    container.push(API.wall.get({{domain:"{1}", count:100, filter:"all", offset:offset}}));
                    offset = offset + 100;
                    iter = iter - 1;
                }};
                return container;
            '''.format(1 + i * 2500, group))
            for response_entity in response:
                for item in response_entity['items']:
                    if self.__is_text_interesting(item['text']):
                        interesting_posts.append('https://vk.com/{0}?w=wall{1}_{2}'.format(group, item['owner_id'], item['id']))
        return interesting_posts
