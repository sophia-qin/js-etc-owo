#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="teamowo"
# This variable dictates whether or not the3 bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

# ~~~~~============== FUNCTIONS ==============~~~~~
def add_to_exchange(price, size, direction, symbol, exchange):
    global order_id
    generate_order_id()
    #print({"type": "add", order_id: order_id, "symbol": symbol, "dir": direction, "price": price, "size": size})
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": direction, "price": price, "size": size})

# buy a stock at price
def buy_stock(price, size, symbol):
    if not validate_symbol(symbol):
        print("INVALID BUY SYMBOL")
        return
    print("BUYING " + symbol)
    add_to_exchange(price, size, "BUY", symbol, exchange)

def buy_stock_XLF(price, size, symbol):
    print("HIIIIIIIIIIIIII")
    if not validate_symbol(symbol):
        print("INVALID BUY SYMBOL")
        return
    print("BUYING " + symbol)
    add_to_exchange(price, size, "BUY", symbol, exchange)

def sell_stock(price, size, symbol):
    if not validate_symbol(symbol):
        print("INVALID SELL SYMBOL")
        return
    print("SELLING " + symbol)
    add_to_exchange(price, size, "SELL", symbol, exchange)

# ~~~~~============== PARSING MESSAGES ==============~~~~~
'''
Takes in a bond dictionary message, returns the bond price
'''
def parse_message(message):
    if message["type"] == "book":
        parse_book(message)
    elif message["type"] == "fill":
        parse_fill(message)


#buy at lowest price, selling for a little bit more than current lowest sell price, but making sure that the sell price > buy price

def parse_book(message):
    if message["symbol"] == "BOND":
        # get the price and try to buy the lowest
        update_stock_values(message) # this is bond, please update haha
        bond_market_sell_prices = message["sell"]
        bond_market_buy_prices = message["buy"]
        '''
        if len(bond_market_sell_prices) > 0:
            # someone is only selling, so we can buy if the price is right
            bond_lowest_sell = bond_market_sell_prices[0][0]
            bond_lowest_sell_amount = bond_market_sell_prices[0][1]
            if bond_lowest_sell < 1001:
                buy_bond(bond_lowest_sell, min(bond_lowest_sell_amount, 100 - inventory['BOND'])) # can only have 100 bonds max
        if len(bond_market_buy_prices) > 0:
            bond_highest_buy = bond_market_buy_prices[0][0]
            bond_highest_buy_amount = bond_market_buy_prices[0][1]
        '''
            # someone is only buying, so we can try to sell to them
        if len(bond_market_sell_prices) == 0 or len(bond_market_buy_prices) == 0:
            return
        bond_lowest_sell = bond_market_sell_prices[0][0]
        bond_lowest_sell_amount = bond_market_sell_prices[0][1]
        bond_highest_buy = bond_market_buy_prices[0][0]
        bond_highest_buy_amount = bond_market_buy_prices[0][1]
        if bond_lowest_sell < 1001:
            buy_stock(bond_lowest_sell, min(bond_lowest_sell_amount, 100 - inventory['BOND']), "BOND") # can only have 100 bonds max
            sell_stock(max(bond_lowest_sell + 1, bond_highest_buy), inventory['BOND']/2, "BOND")

    elif message["symbol"] == "VALBZ":
        valbz_market_sell_prices = message["sell"]
        valbz_market_buy_prices = message["buy"]

        if len(valbz_market_sell_prices) < 1 or len(valbz_market_buy_prices) < 1:
            return
        valbz_lowest_sell = valbz_market_sell_prices[0][0]
        valbz_lowest_sell_amount = valbz_market_sell_prices[0][1]
        valbz_highest_buy = valbz_market_buy_prices[0][0]
        valbz_highest_buy_amount = valbz_market_buy_prices[0][1]
        #if valbz_lowest_sell < 1001:
        buy_stock(valbz_lowest_sell, min(valbz_lowest_sell_amount, 100 - inventory['VALE']), "VALE") # can only have 100 valbzs max
        sell_stock(max(valbz_lowest_sell + 1, valbz_highest_buy), int(inventory['VALE']/3), "VALE")

        #valbz_lowest_sell_VALBZ = message["sell"]
        #valbz_highest_buy_VALBZ = message["buy"]
        #if len(valbz_lowest_sell__VALBZ) == 0 or len(valbz_highest_buy_VALBZ == 0):
        #    return
        #valbz_highest_buy_VALBZ_amount = valbz_highest_buy_VALBZ[0][0]
        #valbz_lowest_sell_VALBZ_amount = valbz_lowest_sell_VALBZ[0][0]
    elif (message["symbol"] == "GS" or message["symbol"] == "MS" or message["symbol"] == "WFC" or message["symbol"] == "BOND"):
        update_stock_values(message)

    if message["symbol"] == "GS":
        gs_market_sell_prices = message["sell"]
        gs_market_buy_prices = message["buy"]

        if len(gs_market_sell_prices) < 1 or len(gs_market_buy_prices) < 1:
            return
        gs_lowest_sell = gs_market_sell_prices[0][0]
        gs_lowest_sell_amount = gs_market_sell_prices[0][1]
        gs_highest_buy = gs_market_buy_prices[0][0]
        gs_highest_buy_amount = gs_market_buy_prices[0][1]
        #if valbz_lowest_sell < 1001:
        buy_stock(gs_lowest_sell, min(gs_lowest_sell_amount, 100 - inventory['GS']), "GS") # can only have 100 valbzs max
        sell_stock(max(gs_lowest_sell + 1, gs_highest_buy), int(inventory['GS']/3), "GS")

    if message["symbol"] == "MS":
        ms_market_sell_prices = message["sell"]
        ms_market_buy_prices = message["buy"]


        if len(ms_market_sell_prices) < 1 or len(ms_market_buy_prices) < 1:
            return
        ms_lowest_sell = ms_market_sell_prices[0][0]
        ms_lowest_sell_amount = ms_market_sell_prices[0][1]
        ms_highest_buy = ms_market_buy_prices[0][0]
        ms_highest_buy_amount = ms_market_buy_prices[0][1]
        #if valbz_lowest_sell < 1001:
        buy_stock(ms_lowest_sell, min(ms_lowest_sell_amount, 100 - inventory['MS']), "MS") # can only have 100 valbzs max
        sell_stock(max(ms_lowest_sell + 1, ms_highest_buy), int(inventory['MS']/3), "MS")

    elif message['symbol'] == 'XLF':
        # weighted average of recent_buy_prices and recent_sell_prices
        xlf_market_sell_prices = message['sell']
        xlf_market_buy_prices = message['buy']
        if len(xlf_market_sell_prices) < 1 or len(xlf_market_buy_prices) < 1:
            return
        xlf_lowest_sell = xlf_market_sell_prices[0][0]
        xlf_lowest_sell_amount = xlf_market_sell_prices[0][1]
        xlf_highest_buy = xlf_market_buy_prices[0][0]
        xlf_highest_buy_amount = xlf_market_buy_prices[0][1]

        if check_recents():
            gs_average_price = int(recent_buy_prices["GS"] + recent_sell_prices["GS"])/2
            ms_average_price = int(recent_buy_prices['MS'] + recent_sell_prices['MS'])/2
            bond_average_price = int(recent_buy_prices["BOND"] + recent_sell_prices["BOND"])/2
            wfc_average_price = int(recent_buy_prices["WFC"] + recent_sell_prices["WFC"])/2
            xlf_fair_price = gs_average_price * 0.2 + ms_average_price * 0.3 + bond_average_price * 0.3 + wfc_average_price * 0.2
            buy_stock(int(xlf_fair_price - 1), 2, 'XLF')
            sell_stock(int(xlf_fair_price + 1), int(inventory['XLF'] / 2), "XLF")

            #xlf_buy_price = int(recent_buy_prices["GS"] * 0.2 + recent_buy_prices["MS"] * 0.3 + recent_buy_prices["BOND"] * 0.3 + recent_buy_prices["WFC"] * 0.2)
            #print(xlf_buy_price)
            #xlf_sell_price = int(recent_sell_prices["GS"] * 0.2 + recent_sell_prices["MS"] * 0.3 + recent_sell_prices["BOND"] * 0.3 + recent_sell_prices["WFC"] * 0.2)
            #print(xlf_sell_price)
            #xlf_buy_amount = int(recent_buy_amounts["GS"] * 0.2 + recent_buy_amounts["MS"] * 0.3 + recent_buy_amounts["BOND"] * 0.3 + recent_buy_amounts["WFC"] * 0.2)
            #print(xlf_buy_amount)
            #xlf_sell_amount = int(recent_sell_amounts["GS"] * 0.2 + recent_sell_amounts["MS"] * 0.3 + recent_sell_amounts["BOND"] * 0.3 + recent_sell_amounts["WFC"] * 0.2)
            #print(xlf_sell_amount)

            #buy_stock(xlf_sell_price,  xlf_sell_amount, "XLF")
            #buy_stock(xlf_lowest_sell, xlf_lowest_sell_amount, 'XLF')
            #sell_stock(xlf_sell_price, int(inventory['XLF'] / 2), "XLF")
        #    sell_stock(max(xlf_buy_price, xlf_highest_buy_amount), int(inventory['XLF'] / 3) -3, "XLF")

            #buy_stock(xlf_buy_price, min(100 - inventory["XLF"], 1), "XLF")
            #sell_stock(xlf_sell_price, max(int(inventory["XLF"]/3), 3), "XLF")
            #buy_stock(xlf_buy_price, 100 - inventory["XLF"], "XLF")
            #sell_stock(xlf_sell_price, int(inventory["XLF"]/3), "XLF")

def update_stock_values(message): # GS, MS, WFC, BOND
    symbol = message['symbol']
    market_sell_prices = message["sell"]
    market_buy_prices = message["buy"]

    if len(market_sell_prices) < 1 or len(market_buy_prices) < 1:
        return
    lowest_sell = market_sell_prices[0][0]
    lowest_sell_amount = market_sell_prices[0][1]
    highest_buy = market_buy_prices[0][0]
    highest_buy_amount = market_sell_prices[0][1]
    recent_buy_prices[symbol] = highest_buy
    recent_sell_prices[symbol] = lowest_sell
    recent_buy_amounts[symbol] = highest_buy_amount
    recent_sell_amounts[symbol] = lowest_sell_amount


def parse_fill(message):
    amount = message['size']
    symbol = message['symbol']
    if message['dir'] == 'SELL':
        amount *= -1
    inventory[symbol] += amount


# ~~~~~============== MISC ==============~~~~~

#shows-availability-introduction-estimate

# returns t/f if symbol is valid
def validate_symbol(symbol):
    return symbol in symbols

def check_recents():
    return recent_buy_prices['BOND'] != 0 and recent_buy_prices['GS'] != 0 and recent_buy_prices['MS'] != 0 and recent_buy_prices['WFC'] != 0 \
        and recent_sell_prices['BOND'] != 0 and recent_sell_prices['GS'] != 0 and recent_sell_prices['MS'] != 0 and recent_sell_prices['WFC'] != 0 \
        and recent_buy_amounts['BOND'] != 0 and recent_buy_amounts['GS'] != 0 and recent_buy_amounts['MS'] != 0 and recent_buy_amounts['WFC'] != 0 \
        and recent_sell_amounts['BOND'] != 0 and recent_sell_amounts['GS'] != 0 and recent_sell_amounts['MS'] != 0 and recent_sell_amounts['WFC'] != 0

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    global exchange, order_id
     # dictionary mapping 'stocks' to amount of each stock
    global inventory
    global symbols
    global recent_sell_prices, recent_buy_prices, recent_buy_amounts, recent_sell_amounts
    recent_sell_prices = {'BOND':0, 'GS':0, 'MS':0, 'WFC':0, 'XLF':0}
    recent_buy_prices = {'BOND':0, 'GS':0, 'MS':0, 'WFC':0, 'XLF':0}
    recent_sell_amounts = {'BOND':0, 'GS':0, 'MS':0, 'WFC':0, 'XLF':0}
    recent_buy_amounts = {'BOND':0, 'GS':0, 'MS':0, 'WFC':0, 'XLF':0}
    order_id = 0
    inventory = {'BOND':0, 'VALBZ':0, 'VALE':0, 'GS':0, 'MS':0, 'WFC':0, 'XLF':0}
    symbols = set(['BOND', 'VALBZ', 'VALE', 'GS', 'MS', 'WFC', 'XLF'])
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    while True:
        msg = read_from_exchange(exchange)
        print("The exchange replied:", msg, file=sys.stderr)
        parse_message(msg)


def generate_order_id():
    global order_id
    order_id = order_id + 1

if __name__ == "__main__":
    main    ()
