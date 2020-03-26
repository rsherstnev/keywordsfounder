import math
import re
import vk_api


class VKGrabber:

    def __init__(self, login, password, key_words):
        self.__key_words = key_words
        self.__vk_session = vk_api.VkApi(login=login, password=password)
        self.__vk_session.auth()
        self.__vk = self.__vk_session.get_api()

    def __is_post_interesting(self, post):
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
            execute_code = '''
                    var massive = [];
                    var offset = ''' + str(1 + 2500 * i) + ''';
                    var iter = 25;
                    while (iter != 0){
                        massive.push(API.wall.get({"domain":"''' + group + '''","count":100, "filter":"all", offset:offset}));
                        offset = offset + 100;
                        iter = iter - 1;
                    };
                    return massive;
            '''
            response = self.__vk.execute(code=execute_code)
            for response_entity in response:
                for item in response_entity['items']:
                    if self.__is_post_interesting(item['text']):
                        interesting_posts.append('https://vk.com/' + str(group) + '?w=wall' + str(item['owner_id'])
                                                 + '_' + str(item['id']))
        return interesting_posts
