import json
from time import sleep, ctime

import requests

from settings import params, user_id_glob


def friends_list(params, user_id_glob):
    """
    Получаем список id друзей пользователя
    """
    params['user_id'] = user_id_glob
    response = requests.get('https://api.vk.com/method/friends.get', params)
    return (response.json())['response']['items']


def user_groups(params, user_id_glob):
    """
    Получаем группы пользователя
    """
    params['count'] = '1000'
    params['extended'] = '0'
    params['user_id'] = user_id_glob
    response = requests.get('https://api.vk.com/method/groups.get', params)
    return response.json()


def personal_group(params, friends_list, user_id_glob):
    """
    Получаем группы пользователя,
    получаем группы друзей,
    получаем уникальные группы, которые есть
    у пользователя, но нет у его друзей
    """
    user_groups_set = set(user_groups(params, user_id_glob)['response']['items'])  # список групп пользователя
    i = 0
    friends_groups_set = None
    for user in friends_list:
        i += 1
        x = user_groups(params, user)  # список групп друга
        if x.get('error', 'active') == 'active':  # делаем проверку на error
            friends_groups_set = set(x['response']['items'])  # преобразуем в множество
        # находим уникальные группы из 2-х множеств которые принадлежат только 1
        user_groups_set = user_groups_set - friends_groups_set
        # печать процесса
        print('\rПроверенно друзей {} из {}'.format(i, len(friends_list)), end='', flush=True)
        sleep(1)

    return user_groups_set


def group_info(params, group_ids):
    """
    Получаем информацию о группах,
    готовим список для преобразования в json
    """
    params['group_ids'] = ','.join(map(str, group_ids))
    params['fields'] = 'members_count'
    response = requests.get('https://api.vk.com/method/groups.getById', params)
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
    print('Начало работы скрипта', ctime())
    print('-------------------------')
    friends_list = friends_list(params, user_id_glob)
    print('Список друзей сформирован', ctime())
    print('Друзей', len(friends_list))
    print('-------------------------')
    print('Процесс проверки друзей')
    sleep(1)
    personal_group = (personal_group(params, friends_list, user_id_glob))
    print()
    print('-------------------------')
    sleep(1)
    print('У данного пользователя {} уникальных групп из {}'
          .format(len(personal_group), len(user_groups(params, user_id_glob)['response']['items']))
          )
    write_json(group_info(params, personal_group))
    print('-------------------------')
    print('Список групп находиться в файле groups.json')
    print('-------------------------')
    print('Конец работы скрипта', ctime())
