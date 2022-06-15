import requests
from logger import fmt
import buff
from utils import send

tm_v2 = "https://market.csgo.com/api/v2/"

session_tm = requests.session()


def minimal_price_(api, item_name):
    req = send(session_tm, "get", f"{tm_v2}search-item-by-hash-name?key={api}&hash_name={item_name}")
    try:
        minimal = req['data'][0]["price"] / 100
    except Exception as e:
        fmt(f'Ошибка при минимальной цене: {e}')
        minimal = 1
    return item_price_info(api, item_name,
                           minimal)


def item_price_info(api, item_name, minimal_price):
    d = send(session_tm, "get", f"{tm_v2}get-list-items-info?key={api}&list_hash_name[]={item_name}")
    a = []
    try:
        for x in d["data"][item_name]['history']:
            if d["data"][item_name]['average'] * 0.9 < x[1]:
                if d["data"][item_name]['average'] * 1.1 > x[1]:
                    a.append(round(x[1]))

        a_set = set(a)
        most_common = None
        qty_most_common = 0

        for item in a_set:
            qty = a.count(item)
            if qty > qty_most_common:
                qty_most_common = qty
                most_common = item

        if most_common < minimal_price:
            total = (minimal_price - most_common) / 2 + most_common
        else:
            total = (most_common - minimal_price) / 5 + minimal_price

        return total
    except Exception as e:
        fmt(f"Ошибка при парсе на тме: {e}")
        return 0


def item_buy_analyse(api, item_name, buff_price, percent, rates, session, keys):
    tm_price = minimal_price_(api, item_name)
    print(tm_price)
    max_price = round((tm_price / percent) / rates["cny"], 2)
    if max_price > float(buff_price['items'][0][1]):
        print(f"Предмет: {item_name} | max_buy: {max_price} | buff_price: {float(buff_price['items'][0][1])}")
        return buff.buy_item(session, buff_price, max_price, keys)
    else:
        print(
            f"НЕ ПОДОШЕЛ-> Предмет: {item_name} | max_buy: {max_price} | buff_price: {float(buff_price['items'][0][1])}")