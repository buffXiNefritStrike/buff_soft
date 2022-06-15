import json
import random
import time

import requests
from bs4 import BeautifulSoup as bs
import utils
from utils import send
from logger import fmt
import steam

buff_market = "https://buff.163.com/api/market/"


def create_session(steam_data, proxy):
    s = requests.Session()
    s.proxies = proxy
    s.cookies.update(steam_data)
    return s


def buff_rates(session):
    data = '{"buff_price_currency":"RUB"}'
    url = 'https://buff.163.com/account/api/prefer/buff_price_currency'
    send(session, "post", url, data=data, headers=utils.header_generate(session.cookies.get_dict()['csrf_token']))
    params = (
        ('_', time.time()),
    )
    res = send(session, 'get', 'https://buff.163.com/account/api/user/info', params=params)
    return {
        "cny": res['data']['buff_price_currency_rate_base_cny'],
        "usd": res['data']['buff_price_currency_rate_base_usd']
    }


def buff_balance(session):
    params = (
        ('_', time.time()),
    )
    return float(
        send(session, "get", 'https://buff.163.com/api/asset/get_brief_asset/', params=params)["data"]["alipay_amount"])


def session_check(session):
    params = (
        ('_', time.time()),
    )
    if send(session, "get", 'https://buff.163.com/api/asset/get_brief_asset/', params=params)[
        'code'] == 'Login Required':
        return True


def buff_auth(steam_data, proxy):
    while True:
        try:
            s = create_session(steam_data, proxy)
            resp = s.get('https://buff.163.com/account/login/steam?back_url=/account/steam_bind/finish').text
            soup = bs(resp, 'html.parser')
            action = soup.select('input[name="action"]')[0]['value']
            openidmode = soup.select('input[name="openid.mode"]')[0]['value']
            openidparams = soup.select('input[name="openidparams"]')[0]['value']
            nonce = soup.select('input[name="nonce"]')[0]['value']
            datas = {
                "action": action,
                "openid.mode": openidmode,
                "openidparams": openidparams,
                "nonce": nonce
            }
            s.post('https://steamcommunity.com/openid/login', data=datas)
            login_data = s.cookies.get_dict()
            if 'session' and "csrf_token" in login_data:
                fmt('Логин на бафф был совершен успешно')
            else:
                fmt('Не получилось сделать логин')
            return s
        except Exception as e:
            fmt(f'Ошибка при авторизации на баффе: {e}')
            time.sleep(5)


def item_price_sorting(session, item_id: str, listings):
    list_of_items = {'goods_id': item_id, 'items': []}
    for sd in range(5):
        try:
            params = (
                ('game', 'csgo'),
                ('goods_id', item_id),
                ('page_num', sd),
                ('sort_by', 'price.asc'),
                ('mode', ''),
                ('allow_tradable_cooldown', '1'),
            )
            r = send(session, 'get', f'{buff_market}goods/sell_order', params=params)
            if r['code'] == 'OK':
                for x in r['data']['items']:
                    listings.append((x['id'], x['price']))
                list_of_items.update({'goods_id': item_id, 'items': listings})
        except:
            pass
    return list_of_items


def generate_fake_s():
    data = json.load(open('C:\\soft_data\\Fakes\\data_fakes.json'))
    while True:
        try:
            rand = random.choice(list(data.keys()))
            mafile = data[rand]
            proxies = utils.get_proxy(utils.get_proxy_api(), 'fake', list_proxy=True)
            proxy = random.choice(proxies)
            proxies = {
                "http": proxy,
                "https": proxy
            }
            sess = create_session({"session": mafile['session'], "csrf_token": mafile['csrf_token']}, proxies)
            req = session_check(sess)
            if req is True:
                fmt('Нужен релогин для фэйк акка')
                acc_data = json.load(open(f'C:\\soft_data\\Fakes\\{rand}'))
                fake_steam = steam.steam_login_fake(proxies, acc_data, f'C:\\soft_data\\Fakes\\{rand}')
                if fake_steam != 0:
                    buff_s = buff_auth(fake_steam, proxies)
                    data.update({rand: {"session": buff_s.cookies.get_dict()['session'],
                                        "csrf_token": buff_s.cookies.get_dict()['csrf_token']}})
                    fmt(f'Оформили релогин для: {rand}')
                    utils.change_file('C:\\soft_data\\Fakes\\data_fakes.json', data)
                    return buff_s
            else:
                return sess
        except Exception as e:
            fmt(f'Ошибка при входе в фейк акк: {e}, acc: {rand}')


def get_price(item, item_id=None):  # обработка на none вывод\
    session = generate_fake_s()
    params = (
        ('game', 'csgo'),
        ('search', item),
    )
    r = send(session, 'get', f'{buff_market}goods', params=params)
    if r['code'] == 'OK':
        for x in r['data']['items']:
            if x['market_hash_name'] == item:
                item_id = x['id']

    if item_id is not None:
        d = item_price_sorting(session, item_id, [])
        if len(d['items']) != 0:
            return d
    else:
        fmt(f'Не нашли item_id предмета: {item}')


def check_avb_buy(session, params):
    res = send(session, 'get', f'{buff_market}goods/buy/preview', params=params)
    if res['code'] == 'OK':
        if res['data']['pay_methods'][0]["enough"] is True:
            return True
        elif res['data']['pay_methods'][0]["enough"] is False:
            return 'NotEnoughBalance'


def item_search(session, order):
    paramas = (
        ("page_num", 1),
        ("page_size", 1),
        ("search", order),
        ("game", "csgo"),
        ("appid", 730)
    )
    session.get("https://buff.163.com/api/market/buy_order/history", params=paramas)
    return session


def mobile_confirm(session, keys, order):
    data = {
        "buyer_info": keys['buff'],
        "bill_orders": ["" + order + ""]}
    session = item_search(session, order)
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://buff.163.com/goods/763310?from=market',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        "X-CSRFToken": session.cookies.get_dict()["csrf_token"]
    }

    r = send(session, "post", "https://buff.163.com/api/market/manual_plus/buyer_send_offer", data=data,
             headers=headers)
    if r['code'] == 'OK' and r['msg'] is None:
        fmt(f'Успешно подтвердили покупку: {order} в приложении')


def asc_seller(session, goods_id, headers, keys):
    data = '{"bill_orders":["' + goods_id + '"],"game":"csgo"}'
    send(session, "post", 'https://buff.163.com/api/market/bill_order/ask_seller_to_send_offer', headers=headers,
         data=data)

    # buy_history(session, keys)


def buying(session, data_a, goods_id, keys):
    data = {"game": "csgo", "goods_id": goods_id, "sell_order_id": data_a[0], "price": data_a[1], "pay_method": 3,
            "allow_tradable_cooldown": 0, "token": "", "cdkey_id": ""}
    headers = utils.header_generate(session.cookies.get_dict()['csrf_token'])
    response = send(session, 'post', f'{buff_market}goods/buy', json=data, headers=headers)
    if response['code'] == 'OK':
        fmt(f'Успешно был куплен предмет: {data_a[0]}')
        asc_seller(session, response['data']['id'], headers, keys)
        utils.dump_item(data_a[0])
    else:
        fmt(f'Ошибка при покупке вещи: {response}')


def buy_item(session, items, max_buy_price, keys):
    returning_list = []
    for x in items['items']:
        if float(x[1]) < max_buy_price:
            try:
                params = (
                    ('game', 'csgo'),
                    ('sell_order_id', x[0]),
                    ('goods_id', items['goods_id']),
                    ('price', x[1]),
                    ('allow_tradable_cooldown', '0'),
                    ('cdkey_id', ''),
                    ('_', time.time()),
                )
                # result = check_avb_buy(session, params)
                # if result != 'NotEnoughBalance':
                returning_list.append((x, items['goods_id']))
                # buying(session, x, items['goods_id'], keys)
                # else:
                # fmt('Недостаточно баланса для покупки вещи')
                # break
            except Exception as e:
                fmt(f'Фатальная ошибка скрипта: {e}')

    fmt(f'Сформировали лист для покупок. Кол-во: {len(returning_list)}')
    return returning_list
    # fmt(f'Закончили покупку вещи: {items["goods_id"]}')


def buy_history(session, keys):
    d = send(session, 'get', f"{buff_market}buy_order/history?page_num=1&page_size=200&game=csgo&appid=730")
    for x in d['data']['items']:
        if x['state_text'] == 'Waiting for your offer':
            fmt(f'Был обнаружен оффер, который нужно подтвердить: {x["id"]}')
            mobile_confirm(session, keys, x['id'])
        elif x['state_text'] == '等待你发起报价':
            fmt(f'Был обнаружен оффер, который нужно подтвердить: {x["id"]}')
            mobile_confirm(session, keys, x['id'])


def confirm(tradeid, steam_client):
    try:
        if steam_client.accept_trade_offer(tradeid)['success']:
            fmt(f'Подтвердили трейд: {tradeid}')
    except Exception as e:
        print(f'err1: {e}')
        pass


def parse_sell_keys(session, steam_s):
    fmt('Была запущена автопередача ключей')
    while True:
        if steam_s.is_session_alive():
            try:
                trades = send(session, 'get', "https://buff.163.com/api/market/steam_trade")
                if trades['code'] == 'OK':
                    if len(trades['data']) >= 1:
                        fmt(f'Нашли трейды для передачи ключей в кол-ве: {len(trades["data"])} штук')
                        for x in trades['data']:
                            tradeid = x['tradeofferid']
                            confirm(tradeid, steam_s)
            except Exception as e:
                fmt(f'Ошибка при парсе на передачу предметов: {e}')
                continue
        else:
            fmt('Сессия слетела, делаем релогин для нее [keys parse]')
            steam_s = steam.steam_login()[0]
        time.sleep(120)


def pages(session):
    returner = []
    for x in range(7):
        try:
            res = send(session, 'get',
                       f'https://buff.163.com/api/market/buy_order/history?page_num={x}&page_size=24&game=csgo&appid=730')
            for k in res['items']:
                print(k['state_text'])
                if k['state_text'] == 'Waiting for seller to send' or k['state_text'] == '等待卖家发起报价':
                    if k['deliver_expire_timeout'] < 36000:
                        fmt(f'Нашли ордер для отмены: {k["id"]}')
                        returner.append(k["id"])
        except:
            continue
    return returner


def cancel_order(session, order_id):
    params = (
        ('game', 'csgo'),
        ('bill_order_id', order_id),
        ('_', round(time.time())),
    )
    preview = send(session, 'get', 'https://buff.163.com/api/market/bill_order/deliver/cancel/preview', params=params)

    if preview['code'] == 'OK':
        data = {"game": "csgo", "bill_order_id": order_id}

        response = send(session, 'post', 'https://buff.163.com/api/market/bill_order/deliver/cancel',
                        headers=utils.header_generate(session.cookies.get_dict()['csrf_token']), json=data)
        return response['code']


def checker_trades(session):
    while True:
        try:
            data = pages(session)
            if len(data) >= 1:
                fmt(f'Нашли предметы для отмены: {len(data)}')
                for x in data:
                    fmt(f'Результат отмены ордера: {x} | {cancel_order(session, x)}')
        except Exception as e:
            fmt(f'Ошибка при парсе покупок на баффе и их отмену: {e}')
