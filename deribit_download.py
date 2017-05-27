#!/usr/bin/python3


from deribit_api import RestClient
import websocket
import json
import datetime
from my_model import *
import syslog
import time
import sys
import os


def float_or_m1(thing):
    try:
        return float(thing)
    except:
        return -1

def main():

    client = RestClient("CSNAPH9dfTzg", "JGDPSFIQFZXNGROTOVTKW3RXBFWPNHA2")
    client.i = 0

    # get existing instruments 
    instruments = { i.ticker : i.id for i in Instrument.select() }

    # create a loop in case we get disconnected
    def on_message(ws, message):
        if message == '{"id":-1,"result":"pong"}':
            return

        client.i = client.i+1
        try:
            data = json.loads(message)
        except:
            return

        if 'notifications' not in data:
            return
        
        ms_out = data['msOut']
        for n in data['notifications']:
            if n['message'] != 'order_book_event':
                continue
            

            result = n['result']
            instrument_name = result['instrument']
            if instrument_name in instruments:
                instrument = instruments[instrument_name]
            else:
                instrument = Instrument.create(ticker = instrument_name)
                instruments[instrument_name] = instrument
            update = OrderBookUpdate.create(ms_out=ms_out, instrument = instrument)
            summary = Summary.create(
                high = float_or_m1(result['high']), 
                low = float_or_m1(result['low']), 
                last = float_or_m1(result['last']),
                update=update
                )
            for bid in result['bids']:
                ob_entry = OrderBook.create(
                    is_bid = True,
                    cm = bid['cm'],
                    price=bid['price'],
                    qty = bid['quantity'],
                    update = update
                )
            for ask in result['bids']:
                ob_entry = OrderBook.create(
                    is_bid = False,
                    cm = ask['cm'],
                    price= ask['price'],
                    qty = ask['quantity'],
                    update = update
                )
            
            

        if client.i % 100 == 0:
            data = {
                'id' :-1,
                'action': '/api/v1/public/ping',
                'arguments' : {}
            }
            data['sig'] = client.generate_signature(data['action'], data['arguments'])
            ws.send(json.dumps(data))

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print('subscription closed!')

    def on_open(ws):
        data = {
            "id": 5533, 
            "action": "/api/v1/private/subscribe",  
            "arguments": {
                "instrument": ["options"],
                "event": ["order_book"] 
            }
        }
        data['sig'] = client.generate_signature(data['action'], data['arguments'])

        ws.send(json.dumps(data))

    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://www.deribit.com/ws/api/v1/",
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)
    ws.on_open = on_open # not sure why this was on another line, it was like this in the example 
    ws.run_forever()


if __name__ == "__main__":
    for i in range(10):
        main()
        try:
            time.sleep(3)
        except:
            sys.exit()