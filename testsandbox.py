import gdax as gdax
import datetime
import time


def get_data(currency_pair, start_time, end_time, granularity): #granularity in seconds, start and end times are python datetimes
    MAX_CANDLES=200 #max datapoints to return per iteration
    pub_gdax=gdax.PublicClient()
    repetition_duration=datetime.timedelta(seconds=(granularity*MAX_CANDLES))
    repetitions=int ((end_time-start_time).seconds /( granularity*MAX_CANDLES)) #number of total repetitions

    result=[]
    current_time=start_time
    while True:
        try:
            if repetitions == 0: #no reps left, set end time of metho dcall to the end time
                ret=pub_gdax.get_product_historic_rates(product_id=currency_pair,start=current_time.isoformat(), end=datetime.datetime.now().isoformat(), granularity=60) 
            else: #still have at least one more rep left
                ret=pub_gdax.get_product_historic_rates(product_id=currency_pair,start=current_time.isoformat(), end=(current_time+repetition_duration).isoformat(), granularity=60)
                current_time=current_time+repetition_duration
                time.sleep(5)
            repetitions-=1
        except:
            print("Error getting gdax historical records")
            return None

        if not isinstance(ret, list):
            print("Error getting gdax historical records. GDAX says " + ret['message'])
            return None    

        for line in ret:
            result.append(""+datetime.datetime.fromtimestamp(line[0]).isoformat()+","+str(line[4]))
        
        if repetitions ==-1:
            break
        
    return result
        
        

                


def main():

    r=get_data(currency_pair="BTC-USD", start_time=(datetime.datetime.now()-datetime.timedelta(hours=20)), end_time=datetime.datetime.now(), granularity=60)

    pub_gdax=gdax.PublicClient()
    a=pub_gdax.get_product_historic_rates("BTC-USD",start="2017-11-23T08:10:38.486348", end=datetime.datetime.now().isoformat(), granularity=60)
    b=pub_gdax.get_product_ticker("BTC-USD")
    gclient=gdax.AuthenticatedClient(key="65d979029164f52e33bb2be0a788d8e0",b64secret="MH9BJJytVcxzWotWCgghEpKJDAjRrXm4J9n+9wzbdNiHY8J44x8S536I6uHOX+dO+/+s2+NjB9MroNDgtVPbVw==",passphrase="9f319sdf8qd",
         api_url="https://api-public.sandbox.gdax.com")


    c=gclient.buy(price=200000, size=0.01, time_in_force='GTC', post_only=True, product_id= "BTC-USD")
    d=gclient.get_fills(product_id='BTC-USD')
    e=gclient.get_orders()

    # a=gem.symbols()
    # c=gem.price(symbol='btcusd')
    # d=gem.new_order(amount="5",price="3528.85",side="buy",client_order_id="3424",symbol='btcusd',type='exchange limit', options=["maker-or-cancel"])
    # e=gem.book(symbol='btcusd',limit_asks=0,limit_bids=0)

    anum = int(input("Please enter a number"))


    

if __name__ == "__main__":
    main()



