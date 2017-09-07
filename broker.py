import datetime
import time
import json
import numpy as np
from cryptoDB import CryptoDB
from simplestrat import SimpleStrat
import gdax as gdax
import uuid



class Broker:

    def __init__ (self, cash, currency_pair, key_file, simulation=True, prod_environment=False,**args):
        '''TODO
            Get historic rates for more than 200 entries

        '''

        self.start_time=datetime.datetime.now()
        self.frame_time=datetime.datetime.now()
        self.market_price=0 #market price of current frame
        self.position=0 #cryptopcurrency quantity
        self.cash=cash #cash on hand
        self.currency_pair=currency_pair
        self.strategy=SimpleStrat(self)
        self.last_trade_filled_id=0
        self.completed_orders=[]
        self.recently_filled_orders=[]
        self.cash_limit_filter=100 #USD below which this script is blind to

        self.limit_orders=[]

        self.plotPrice=[]
        self.plotTime=[]
        self.plotBuyTime=[]
        self.plotSellTime=[]
        self.plotBuyPrice=[]
        self.plotSellPrice=[]
        self.plotCash=[] #cash on hand
        self.plotValue=[] #total value of cash + position
        self.plotMVA=[]

        # If this is a simulation, instead of having the current frame be the end of the data list, we 
        # are going to use the frame_index as a pointer to the current frame in the data
        self.simulation=simulation
        self.sim_open_orders=[] #list of dictionaries with, amount, size, price, order_id
        self.sim_completed_orders=[]
        self.sim_frame_index=self.strategy.max_frames_required

        if self.simulation and not args['data']:
            print("ERROR: Simulation flag is true but no data is loaded")
            return
        
        if args['data'] and isinstance(args['data'],list): #data should be in the right tick frequency as the strategy
            self.data=args['data']
        else:  #import data
            cdb=CryptoDB(tableName="cryptoDB")
            delta=datetime.timedelta(minutes=self.strategy.max_frames_required*self.strategy.tick_time.seconds/60 + 60)
            self.data=cdb.getDateRangeData(currency_pair,(self.start_time-delta).isoformat(),self.start_time.isoformat())
        
        self.data_size=len(self.data)

        key_info=None
        with open(key_file) as data_file:    
            key_info = json.load(data_file)

        if prod_environment:
            self.gclient=gdax.AuthenticatedClient(key=key_info['key'],b64secret=key_info['secret'],passphrase=key_info['passphrase'],
                api_url="https://api.gdax.com")          
        else:
            self.gclient=gdax.AuthenticatedClient(key=key_info['test_key'],b64secret=key_info['test_secret'],passphrase=key_info['test_passphrase'],
                api_url="https://api-public.sandbox.gdax.com")

        self.get_recently_filled_orders(True) #we want to set last_trade_filled_id before we get started on ticking
    
    def get_market_price(self):
        if self.simulation:
            return float(self.data[self.sim_frame_index].split(",")[1])
        return float(self.gclient.get_product_ticker(self.currency_pair)['price'])

    def get_mva(self, frames):
        '''Gets the moving average over the last frames amount of frames'''
        if self.simulation:
            return np.mean(list(map((lambda x: float(x.split(",")[1])), self.data[(self.sim_frame_index-frames):(self.sim_frame_index-1)])))    
        return np.mean(list(map((lambda x: float(x.split(",")[1])), self.data[(self.data_size-frames):(self.data_size-1)])))

    def create_order(self, limit_price, amount, direction):
        cash_diff=0
        if direction=='buy' and limit_price < self.market_price:
            if self.cash >= limit_price*amount:
                if self.simulation:
                    order={"side": "buy", "price": limit_price, "size": amount, "created_at": self.frame_time.isoformat(), "id": str(uuid.uuid4())}
                    self.sim_open_orders.append(order)
                    result=order
                else:
                    result=self.gclient.buy(price=limit_price, size=amount, time_in_force='GTC', post_only=True, product_id=self.currency_pair)
                cash_diff-=amount*limit_price

            else:
                print("Warning: not enough cash to buy @market {0} at market price ({1}). Cash remaining: ${2}".format(amount, limit_price, self.cash))
                return -1
        elif direction == 'sell' and limit_price > self.market_price:
            if self.position >= amount:
                if self.simulation:
                    order={"side": "sell", "price": limit_price, "size": amount, "created_at": self.frame_time.isoformat(), "id": str(uuid.uuid4())}
                    self.sim_open_orders.append(order)
                    result=order
                else:
                    result=self.gclient.sell(price=limit_price, size=amount, time_in_force='GTC', post_only=True, product_id=self.currency_pair)
            else:
                print("Warning: not enough position to sell @market {0} at market price ({1}). Position: {2}".format(amount, limit_price, self.position))
                return
        else:
            print ("ERROR creating {} order at {} (perhaps market price no longer allows it?".format(direction, limit_price))
            return 0

        if result.get('id') is None:
            print ("ERROR creating {} order at {}. Message: {}".format(direction, limit_price, result['message']))
            return 0
        if not self.simulation:
            self.limit_orders.append(result)
        self.cash=self.cash+cash_diff
        return result
    
    def get_account_value(self):
        return self.cash+self.position*self.market_price

    def get_active_orders(self):
        if self.simulation:
            return self.sim_open_orders
        temp=(self.gclient.get_orders())[0]
        try:
            result= list(filter(lambda x: x['product_id'] == self.currency_pair and float(x['size'])*float(x['price']) < self.cash_limit_filter, temp))
        except:
            print ("ERROR")
        
        return result

    def get_recently_filled_orders(self, update_last_filled_id=False):
        '''
        Run with update_last_filled_id=true only once per tick, since it modifies update_last_filled_id
        '''

        # If simulation, then make sure we process all the sell ordersorders
        if self.simulation:
            if update_last_filled_id: #if runonce and simulation, process sell orders
                self.sim_completed_orders=[]
                for order in self.sim_open_orders:
                    total_price= float(order['price'])*float(order['size'])
                    if order['side'] == 'sell' and float(order['price']) < self.market_price:
                        print("SOLD at {} (Total:{}) on {}.".format(order['price'], total_price, self.frame_time.isoformat()))
                        self.cash+=total_price
                        self.position-=order['size']
                        self.sim_completed_orders.append(order)
                        self.sim_open_orders.remove(order)
                    if order['side'] == 'buy' and float(order['price']) > self.market_price:
                        print("Bought at {} (Total:{}) on {}.".format(order['price'], total_price, self.frame_time.isoformat()))
                        self.position+=order['size']
                        self.sim_completed_orders.append(order)
                        self.sim_open_orders.remove(order)
            return self.sim_completed_orders


        # not simulation
        fills=self.gclient.get_fills(product_id=self.currency_pair, limit=30)
        result=list(filter(lambda x: x['trade_id'] > self.last_trade_filled_id and 
            float(x['size'])*float(x['price']) < self.cash_limit_filter, fills[0]))

        if self.last_trade_filled_id==0 and fills[0]:
            self.last_trade_filled_id=float(fills[0][0]['trade_id'])
            return []

        #if runonce, then set last_trade_filled_id and then set cash and position balances
        if update_last_filled_id: 
            if fills[0]:
                self.last_trade_filled_id=float(fills[0][0]['trade_id'])
                for o in result:
                    if o['side']=='sell':
                        self.cash+=float(o['price'])*float(o['size'])
                        self.position-=float(o['size'])
                    if o['side']=='buy':
                        self.position+=float(o['size'])

        return result

    def cancel_order(self,order_id):
        if self.simulation:
            result=['boiler_plate']
            for o in self.sim_open_orders:
                if o['id'] == order_id:
                    result=o
                    self.sim_open_orders.remove(o)
            return [result['id']]

        return self.gclient.cancel_order(order_id)


    


    def tick(self):
        if self.simulation:
            self.sim_frame_index+=1
            self.market_price=self.get_market_price()
            self.frame_time=datetime.datetime.strptime(self.data[self.sim_frame_index].split(',')[0],'%Y-%m-%dT%H:%M:%S.%fZ')

        else:
            self.market_price=self.get_market_price()
            self.frame_time=datetime.datetime.now()
            self.data.append(self.frame_time.isoformat()+","+str(self.market_price))
            self.data.pop(0)

        self.limit_orders=self.get_active_orders()
        self.recently_filled_orders=self.get_recently_filled_orders(True)

        
        self.strategy.tick()
        if not self.simulation:
            time.sleep(self.strategy.tick_time.seconds)

        







def main():

    cdb=CryptoDB(tableName="cryptoDB")
    d=cdb.getDateRangeData("LTC-USD", "2017-08-16T01:10:38.486348", '2017-08-21T12:24:27.271083')

    broker=Broker(cash=100, currency_pair="LTC-USD", key_file=".keygx.json", prod_environment=True, simulation=True, data=d)
    
    if broker.simulation:
        total_frame_iterations=broker.data_size-broker.sim_frame_index-1
    else:
        total_frame_iterations=2000

    for number in range(1,total_frame_iterations):
        broker.tick()
    broker.strategy.complete()

if __name__ == "__main__":
    main()
