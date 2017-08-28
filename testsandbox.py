import gdax as gdax
import datetime



def main():
    pub_gdax=gdax.PublicClient()
    a=pub_gdax.get_product_historic_rates("BTC-USD",start="2017-08-23T01:10:38.486348", end=datetime.datetime.now().isoformat(), granularity=600)
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



