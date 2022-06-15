import json

import threading
import buff
import steam
import tm_parser
import utils
from logger import fmt

data_login = steam.steam_login()
settings = json.load(open('C:\\soft_data\\settings.json'))


class Client:
    def __init__(self):
        self.steam_s = data_login[0]
        self.buff_s = buff.buff_auth(data_login[1], data_login[2])
        self.keys = data_login[3]
        self.rates = buff.buff_rates(self.buff_s)
        self.percent = settings['percent']

    def main_worker(self):
        # x = threading.Thread(target=buff.parse_sell_keys, args=(self.buff_s, self.steam_s))
        # x.start()
        # x2 = threading.Thread(target=buff.checker_trades, args=(self.buff_s,))
        # x2.start()

        while True:
            all_items = []
            for x in utils.list_of_items():
                if buff.session_check(self.buff_s) is not True:
                    buff_price = buff.get_price(x)
                    if buff_price is not None:
                        list_of_item = tm_parser.item_buy_analyse(self.keys["tm"], x, buff_price, self.percent,
                                                                  self.rates,
                                                                  self.buff_s, self.keys)
                        try:
                            for it in list_of_item:
                                all_items.append(it)
                        except:
                            pass

                    if buff.buff_balance(self.buff_s) < 10:
                        break
                else:
                    fmt('Необходим релогин для баффа')
                    self.buff_s = buff.buff_auth(data_login[1], data_login[2])

            print(f'items found: {len(all_items)}')
            new_data = utils.checker_items(all_items)
            print(f'items sorted: {len(new_data)}')
            for f in all_items:
                buff.buying(self.buff_s, f[0], f[1], [])


d = Client()
while True:
    d.main_worker()
