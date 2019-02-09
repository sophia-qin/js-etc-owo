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
# This variable dictates whether or not the bot is connecting to the prod
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
            sell_stock(max(bond_lowest_sell + 1, bond_highest_buy), inventory['BOND'], "BOND")

    elif message["symbol"] == "VALBZ":
        #valbz_market_sell_prices = message["sell"]
        #valbz_market_buy_prices = message["buy"#

        if len(bond_market_sell_prices) == 0 or len(bond_market_buy_prices) == 0:
            return
        bond_lowest_sell = bond_market_sell_prices[0][0]
        bond_lowest_sell_amount = bond_market_sell_prices[0][1]
        bond_highest_buy = bond_market_buy_prices[0][0]
        bond_highest_buy_amount = bond_market_buy_prices[0][1]
        if bond_lowest_sell < 1001:
            buy_stock(bond_lowest_sell, min(bond_lowest_sell_amount, 100 - inventory['BOND']), "BOND") # can only have 100 bonds max
            sell_stock(max(bond_lowest_sell + 1, bond_highest_buy), inventory['BOND'], "BOND")

    bond_lowest_sell_VALBZ = message["sell"]
        bond_highest_buy_VALBZ = message["buy"]
        if len(bond_lowest_sell__VALBZ) == 0 or len(bond_highest_buy_VALBZ == 0):
            return
        bond_highest_buy_VALBZ_amount = bond_highest_buy_VALBZ[0][0]
        bond_lowest_sell_VALBZ_amount = bond_lowest_sell_VALBZ[0][0]

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

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    global exchange, order_id
     # dictionary mapping 'stocks' to amount of each stock
    global inventory
    global symbols
    global lowest_sell_prices, highest_buy_prices
    lowest_sell_prices = {'BOND':float('inf'), 'VALBZ':float('inf'), 'VALE':float('inf'), 'GS':float('inf'), 'MS':float('inf'), 'WFC':float('inf'), 'XLF':0}
    highest_buy_prices = {'BOND':0, 'VALBZ':0, 'VALE':0, 'GS':0, 'MS':0, 'WFC':0, 'XLF':0}
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
