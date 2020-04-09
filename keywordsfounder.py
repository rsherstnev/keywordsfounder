import argparse
from getpass import getpass
import os

import vk_api

from vkgrabber import VKGrabber


class MyException(Exception):
    pass


HELP = '''Usage: keywordsfounder.py [--login LOGIN] [--password PASSWORD] [--keywords-file KEYWORDS_FILE]
                          [--groups-file GROUPS_FILE] [--output-file OUTPUT_FILE]

Options:
-h, --help              Вывести данную помощь.
-l, --login             Логин учётной записи Вконтакте, из под которой будут производиться запросы к API VK.
-p, --password          Пароль учётной записи Вконтакте, из под которой будут производиться запросы к API VK.
-k, --keywords-file     Файл, в котором содержатся ключевые слова для фильтрации.
-g, --groups-file       Файл, в котором содержатся группы Вконтакте, в которых будет осуществлен поиск.

Extra options:
-o, --output-file       Файл, в который будут записываться найденные записи групп.
'''

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h', '--help', action='store_true')
parser.add_argument('-l', '--login')
parser.add_argument('-p', '--password')
parser.add_argument('-k', '--keywords-file')
parser.add_argument('-g', '--groups-file')
parser.add_argument('-o', '--output-file')

file = None

try:
    args = parser.parse_args()

    if args.help:
        print(HELP)
        raise SystemExit

    if not args.keywords_file:
        raise MyException('Не указан файл с ключевыми словами для поиска!')

    if not args.groups_file:
        raise MyException('Не указан файл с группами, в которых производить поиск!')

    if not os.path.isfile(args.keywords_file):
        raise MyException('Файл ' + args.keywords_file + ' не был найден!')

    if not os.path.isfile(args.groups_file):
        raise MyException('Файл ' + args.groups_file + ' не был найден!')

    if not args.login:
        args.login = input('Введите логин учетной записи Вконтакте, '
                           'из под которой будут осуществляться запросы к API VK: ')

    if args.login and not args.password:
        args.password = getpass(prompt='Введите пароль от учетной записи Вконтакте с логином ' + args.login + ': ')

    keywords = []
    with open(args.keywords_file, 'r', encoding='utf-8') as file:
        for line in file:
            keywords.append(line.strip())

    grabber = VKGrabber(args.login, args.password, keywords)

    groups = []
    with open(args.groups_file, 'r', encoding='utf-8') as file:
        for line in file:
            group = line.strip()
            if grabber.is_group_exists(group):
                groups.append(group)
            else:
                print(group + ' либо не является группой, либо вообще не существует и будет выпущена из сканирования')

    if args.output_file:
        try:
            file = open(args.output_file, 'x', encoding='utf-8')
        except FileExistsError:
            while True:
                challenge = input('Файл ' + file.name + ' уже существует, хотите переписать его? [Y/N] ')
                if challenge == 'Y' or challenge == 'N':
                    break
            if challenge == 'Y':
                file = open(args.output_file, 'w', encoding='utf-8')
            else:
                raise MyException('Ошибка, запустите скрипт с другим файлом для записи, либо без файла')

    for group in groups:
        interesting_posts = grabber.get_interesting_posts_list(group)
        for interesting_post in interesting_posts:
            if args.output_file:
                print(interesting_post, file=file)
            else:
                print(interesting_post)

except KeyboardInterrupt:
    pass

except vk_api.exceptions.BadPassword:
    print('Введены невалидные учетные данные, повторите попытку')

except MyException as error:
    print(error)

finally:

    try:
        if not file.closed:
            file.close()
    except:
        pass

    if os.path.isfile("./vk_config.v2.json"):
        os.remove('./vk_config.v2.json')
