import os
import argparse
import vk_api

from vkgrabber import VKGrabber


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', '-l',
                        help='Логин учётной записи VK, из под которой будут производиться запросы к API VK')
    parser.add_argument('--password', '-p',
                        help='Пароль учётной записи VK, из под которой будут производиться запросы к API VK')
    parser.add_argument('--keywords-file', '-k',
                        help='Файл, в котором содержатся ключевые слова для фильтрации')
    parser.add_argument('--groups-file', '-g',
                        help='Файл, в котором содержатся группы Вконтакте, в которых будет осуществлен поиск')
    parser.add_argument('--output-file', '-w',
                        help='Файл, в который будут записываться найденные записи групп')

    try:
        args = parser.parse_args()

        if args.keywords_file is None:
            raise Exception('Не указан файл с ключевыми словами для поиска!')

        if args.groups_file is None:
            raise Exception('Не указан файл с группами, в которых производить поиск!')

        if not os.path.isfile(args.keywords_file):
            raise Exception('Файл ' + args.keywords_file + ' не был найден')

        if not os.path.isfile(args.groups_file):
            raise Exception('Файл ' + args.groups_file + ' не был найден')

        if args.login is None:
            args.login = input('Введите логин учетной записи Вконтакте, '
                               'из под которой будут осуществляться запросы к API VK: ')

        if args.login is not None and args.password is None:
            args.password = input('Введите пароль от учетной записи Вконтакте с логином ' + args.login + ": ")

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

        if args.output_file is not None:
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
                    raise Exception('Ошибка, запустите скрипт с другим файлом для записи, либо без файла')

        for group in groups:
            interesting_posts = grabber.get_interesting_posts_list(group)
            for interesting_post in interesting_posts:
                if args.output_file is not None:
                    file.writelines(interesting_post + '\n')
                else:
                    print(interesting_post)

        if not file.closed:
            file.close()

    except vk_api.exceptions.BadPassword:
        print('Введены невалидные учетные данные, повторите попытку')
        raise SystemExit

    except Exception as error:
        print(error)
        raise SystemExit

    finally:
        if os.path.isfile("./vk_config.v2.json"):
            os.remove('./vk_config.v2.json')


if __name__ == "__main__":
    main()