import datetime
import json
import numpy as np
from cryptoDB import CryptoDB
from simplestrat import SimpleStrat
import gdax as gdax



class Broker:

    def __init__ (self, cash, currency_pair, key_file,*data):
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
        
        if data and isinstance(data,list): #data should be in the right tick frequency as the strategy
            self.data=data
        else:  #import data
            cdb=CryptoDB(tableName="cryptoDB")
            delta=datetime.timedelta(minutes=self.strategy.max_frames_required*self.strategy.tick_time.seconds/60 + 60)
            self.data=cdb.getDateRangeData(currency_pair,(self.start_time-delta).isoformat(),self.start_time.isoformat())
        
        self.data_size=len(self.data)

        key_info=None
        with open(key_file) as data_file:    
            key_info = json.load(data_file)

        self.gclient=gdax.AuthenticatedClient(key=key_info['key'],b64secret=key_info['secret'],passphrase=key_info['passphrase'],
            api_url="https://api-public.sandbox.gdax.com")

        self.get_recently_filled_orders(True) #we want to set last_trade_filled_id before we get started on ticking
    
    def get_market_price(self):
        return float(self.gclient.get_product_ticker(self.currency_pair)['price'])

    def get_mva(self, frames):
        '''Gets the moving average over the last frames amount of frames'''
        return np.mean(list(map((lambda x: float(x.split(",")[1])), self.data[(self.data_size-frames):(self.data_size-1)])))
        # temp= []
        # for point in self.data[(self.data_size-frames):(self.data_size-1)]:
        #     temp.append(float(point.split(",")[1]))
        # return np.mean(temp)        


    def create_order(self, limit_price, amount, direction):
        cash_diff=0
        if direction=='buy' and limit_price < self.market_price:
            result=self.gclient.buy(price=limit_price, size=amount, time_in_force='GTC', post_only=True, product_id=self.currency_pair)
            cash_diff-=amount*limit_price
        elif direction == 'sell' and limit_price > self.market_price:
            result=self.gclient.sell(price=limit_price, size=amount, time_in_force='GTC', post_only=True, product_id=self.currency_pair)

        else:
            print ("ERROR creating {} order at {} (perhaps market price no longer allows it?".format(direction, limit_price))
            return 0

        if result.get('id') is None:
            print ("ERROR creating {} order at {}. Message: {}".format(direction, limit_price, result['message']))
            return 0
        self.limit_orders.append(result)
        self.cash=self.cash+cash_diff
        return result
    
    def get_account_value(self):
        return self.cash+self.position*self.market_price

    def get_active_orders(self):
        temp=(self.gclient.get_orders())[0]
        result= list(filter(lambda x: x['product_id'] == self.currency_pair, temp))
        return result

    def get_recently_filled_orders(self, update_last_filled_id=False):
        '''
        Run with update_last_filled_id=true only once per tick, since it modifies update_last_filled_id
        '''
        fills=self.gclient.get_fills(product_id=self.currency_pair, limit=30)
        result=list(filter(lambda x: x['trade_id'] > self.last_trade_filled_id, fills[0]))

        #if runonce, then set last_trade_filled_id and then set cash and position balances
        if update_last_filled_id: 
            if fills[0]:
                self.last_trade_filled_id=float(fills[0][0]['trade_id'])
                for o in result:
                    if o['size']=='sell':
                        self.cash+=float(o['price'])*float(o['size'])
                        self.position-=float(o['size'])
                    if o['side']=='buy':
                        self.position+=float(o['size'])


        return result

    def cancel_order(self,order_id):
        return self.gclient.cancel_order(order_id)


    


    def tick(self):
        self.market_price=self.get_market_price()
        self.frame_time=datetime.datetime.now()
        self.data.append(self.frame_time.isoformat()+","+str(self.market_price))
        self.data.pop(0)
        self.limit_orders=self.get_active_orders()
        self.recently_filled_orders=self.get_recently_filled_orders(True)

        
        self.strategy.tick()







def main():
    broker=Broker(cash=10000,currency_pair="LTC-USD", key_file=".keygx.json")
    while True:
        broker.tick()

if __name__ == "__main__":
    main()
