import time

from steampy.client import SteamClient
import utils
from logger import fmt


def steam_ip_checker(steam_client, proxy):
    req = steam_client._session.get('http://checkip.dyndns.org').text
    if proxy.split("http://")[1].split("@")[1].split(':')[0] in req:
        fmt(f'Прокси: {proxy} ')
        return True


def steam_login():
    fmt('Делаем логин в стим')
    while True:
        keys = utils.mafile_reading()
        print(keys)
        proxies = {
            "http": keys['proxy'],
            "https": keys['proxy']
        }
        try:
            steam_client = SteamClient(keys['api'])
            steam_client._session.proxies = proxies
            while True:
                if steam_ip_checker(steam_client, keys['proxy']) is True:
                    fmt('Ip аккаунта проверен. Продолжается работа')
                    break
                else:
                    fmt('Что-то с сессией/прокси не работают')

            steam_client.login(keys["username"], keys["password"], keys['paths']['maFile'])
            if steam_client.is_session_alive() is True:
                fmt('Успешно был выполнен логин в steam сессию')
                return steam_client, steam_client._get_session_id(), proxies, keys

        except Exception as e:
            fmt(f'Ошибка при логине в стим: {e}')
            if "too many login" in str(e):
                fmt('Куча логинов с прокси. Нужно ее поменять!')
                time.sleep(120)
            elif "incorrect" in str(e):
                fmt('Неверные данные от аккаунта!')
                time.sleep(500)
            elif "Captcha required" in str(e):
                fmt('Captcha required')
                time.sleep(600)
            else:
                fmt('steam other error')
                time.sleep(120)


def steam_login_fake(proxies, keys, path):
    fmt('Делаем логин в стим на фэйк')
    while True:
        try:
            steam_client_ = SteamClient('')
            steam_client_._session.proxies = proxies
            while True:
                if steam_ip_checker(steam_client_, proxies['http']) is True:
                    fmt('Ip аккаунта проверен. Продолжается работа')
                    break
                else:
                    fmt('Что-то с сессией/прокси не работают')

            steam_client_.login(keys["login"], keys["password"], path)
            if steam_client_.is_session_alive() is True:
                fmt('Успешно был выполнен логин в steam сессию')
                return steam_client_._get_session_id()

        except Exception as e:
            fmt(f'Ошибка при логине в стим фейк: {e}')
            return 0