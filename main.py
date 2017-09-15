import json
from time import sleep, ctime
import requests


TOKEN = ''
VERSION = '5.68'
good_error = frozenset([18, 113])
# # user_id_glob = 5030613  # id, указанный в задании
# user_id_glob = 87074577  # id, мой id
# # user_id_glob = 47936997
# params = {'access_token': token, 'v': version}


def check_input_ids():
    """
    Получает айди или идентификатор неважно отправляет get запрос на vk
    и обрабатывает ответ на валидность есть юзер, нет тактого или деактивирован
    если юзер Валиден то возврашает id и отдает в процесс
    """
    while True:
        params = {'access_token': TOKEN,
                  'v': VERSION,
                  'user_ids': input('Введите ID для поиска ')
                  }
        response = requests.get('https://api.vk.com/method/users.get', params)
        if response.json().get('error', 'active') == 'active':
            if response.json()['response'][0].get('deactivated', 'yes') == 'yes':
                valid_id = response.json()['response'][0]['id']
            else:
                print('Пользователь с таким id деактивирован\n')
                continue
            break
        else:
            print('Пользователя с таким id не существует\n')
    return valid_id


def get_get(method, **kwargs):
    """
    Принимает url для get Запроса и параметры, формирует запрос
    и возврашает ответ, а дальше уже его другие функции разбирают
    """
    params = {'access_token': TOKEN, 'v': VERSION}
    for key, value in kwargs.items():
        params[key] = value
    response = requests.get('https://api.vk.com/method/{}'.format(method), params)
    if (response.json()).get('response'):
        good_answer = response
    else:
        if response.json()['error']['error_code'] in good_error:
            good_answer = response
        else:
            print('Возникла ошибка: {}\nОписание: {}'
                  .format(response.json()['error']['error_code'],
                          response.json()['error']['error_msg']))
            exit()

    return good_answer


def friends_list(user_id):
    """
    Вызываем get_json скармливаем ей url и параметры передаваемые в запросе.
    Только список друзей возврашает ID пользователей
    """
    response = get_get('friends.get', user_id=user_id)
    return (response.json())['response']['items']


def user_groups(user_id):
    """
    Вызываем get_json скармливаем ей url и параметры передаваемые в запросе.
    Формирует список групп.
    """
    response = get_get('groups.get', count='1000', extended='0', user_id=user_id)
    return response.json()


def personal_group(friends, user_id):
    """
    Получаем группы пользователя,
    получаем группы друзей,
    получаем уникальные группы, которые есть
    у пользователя, но нет у его друзей
    """
    user_groups_set = set(user_groups(user_id)['response']['items'])  # список групп пользователя
    i = 0
    friends_groups_set = None
    for user in friends:
        i += 1
        x = user_groups(user)  # список групп друга
        if x.get('error', 'active') == 'active':  # делаем проверку на error
            friends_groups_set = set(x['response']['items'])  # преобразуем в множество
        # находим уникальные группы из 2-х множеств которые принадлежат только 1
        user_groups_set = user_groups_set - friends_groups_set
        # печать процесса
        print('\rПроверенно друзей {} из {}'.format(i, len(friends_list)), end='', flush=True)
        sleep(1)

    return user_groups_set


def group_info(group_ids):
    """
    Получаем информацию о группах,
    готовим список для преобразования в json
    """
    response = get_get(
        'groups.getById',
        group_ids=','.join(map(str, group_ids)),
        fields='members_count'
    )
    info_groups_list = []
    for group in (response.json())['response']:
        if group.get('deactivated', 'active') == 'active':
            group_dict = {'name': group['name'], 'gid': group['id'], 'members_count': group['members_count']}
            info_groups_list.append(group_dict)
    return info_groups_list


def write_json(data):
    """
    Записываем список в json
    """
    with open('groups.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=0)


if __name__ == '__main__':
    user_id_glob = check_input_ids()
    print('Начало работы скрипта', ctime())
    print('-------------------------')
    friends_list = friends_list(user_id_glob)
    user_group = user_groups(user_id_glob)['response']['items']
    print('Список друзей и групп пользователя сформирован', ctime())
    print('Друзей {}\nГрупп {}'.format(len(friends_list), len(user_group)))
    print('-------------------------')
    print('Процесс проверки друзей')
    sleep(1)
    personal_group = (personal_group(friends_list, user_id_glob))
    print('-------------------------')
    sleep(1)
    print('У данного пользователя {} уникальных групп из {}'
          .format(len(personal_group), len(user_groups(user_id_glob)['response']['items']))
          )
    write_json(group_info(personal_group))
    print('-------------------------')
    print('Список групп расположен в файле groups.json')
    print('-------------------------')
    print('Конец работы скрипта', ctime())
