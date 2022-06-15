import os, json
import requests
import time


def change_file(f, d):
    with open(str(f), 'w', encoding='utf-8') as file:
        json.dump(d, file, indent=4)
        file.close()


def reading_file(fileName):
    try:
        file = open(fileName, 'r')
        for x in file.readlines():
            if 'Password' in x:
                return x.replace(' ', '').replace("Password:", "").replace('\n', '')

    except FileNotFoundError:
        print(f'Файл: {fileName} не был найден')


def get_proxy_api():
    try:
        file = open("C:\\soft_data\\proxy.txt", 'r')
        for x in file.readlines():
            return x

    except FileNotFoundError:
        time.sleep(1000)
        print(f'Файл: C:\\proxy.txt не был найден!')
        return None


def finding_path():
    data = {}
    for x in os.listdir(os.getcwd()):
        if '.maFile' in x:
            data.update({"maFile": x})
        elif '.txt' in x:
            data.update({"txt": x})
    return data


def mafile_reading():
    paths = finding_path()
    maFile_name = paths['maFile']
    fileName = paths['txt']
    password = reading_file(fileName)
    try:
        file = json.load(open(maFile_name))
        try:
            username = file['account_name']
            api_key = file['api']
            buff_key = file['buff']
            tm_key = file['tm']
        except KeyError:
            print(f'Файл: {maFile_name} не были найдены keys! Необходимо их установить')
            api_key, buff_key, tm_key = input('Введите ваш steam API: '), input('Введите ваш buff key: '), input(
                'Введите ваш steam tm key: ')
            file.update({"steamid": file['Session']['SteamID']})
            file.update({"api": api_key})
            file.update({"buff": buff_key})
            file.update({"tm": tm_key})
            change_file(maFile_name, file)

        return {
            "api": api_key,
            "buff": buff_key,
            "tm": tm_key,
            "username": username,
            "password": password,
            "proxy": get_proxy(get_proxy_api(), username),
            "paths": paths
        }

    except FileNotFoundError:
        print(f'Файл: {maFile_name} не был найден')


def get_proxy(api, account, list_proxy=False):
    d = send(requests.session(), 'get', f'https://proxy-store.com/api/{api}/getproxy/?comment={account}')
    if d['status'] == 'no':
        print(f'У вас нету проксей с комментарием: "{account}"')
        return None
    if list_proxy is False:
        for x in d['list']:
            g = d["list"][x]
            return f'http://{g["user"]}:{g["pass"]}@{g["ip"]}:{g["port"]}'
    else:
        returner = []
        for x in d['list']:
            g = d["list"][x]
            returner.append(f'http://{g["user"]}:{g["pass"]}@{g["ip"]}:{g["port"]}')
        return returner


def send(session, method, url, headers=None, data=None, json=None, params=None):
    if method == 'post':
        while True:
            try:
                return session.post(url, headers=headers, data=data, json=json, params=params).json()
            except Exception as error:
                print(f'Ошибка при запросе post: {url}\n'
                      f'Error: {error}')
                time.sleep(2)

    elif method == 'get':
        while True:
            try:
                return session.get(url, headers=headers, data=data, json=json, params=params).json()
            except Exception as error:
                print(f'Ошибка при запросе get: {url}\n'
                      f'Error: {error}')
                time.sleep(2)


def header_generate(token):
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://buff.163.com',
        'Referer': 'https://buff.163.com/goods/36019?from=market',
    }
    headers.update({'X-CSRFToken': token})
    return headers


def list_of_items():
    return_list = []
    f = open('C:\\soft_data\\items.txt', 'r', encoding='utf-8').readlines()
    for x in f:
        return_list.append(x.replace('\n', ''))
    return return_list


def checker_items(items):
    list_re = []
    with open('C:\\soft_data\\data_of_buy_items.json') as data:
        data = json.load(data)
    for x in items:
        if x[0][0] not in data['items']:
            list_re.append(x)
    return list_re


def dump_item(item):
    with open('C:\\soft_data\\data_of_buy_items.json') as data:
        data = json.load(data)
    d = data['items']
    d.append(item)
    data.update({"items": d})
    change_file('C:\\soft_data\\data_of_buy_items.json', data)