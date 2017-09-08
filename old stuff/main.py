from geminipy import Geminipy




def main():
    gem=Geminipy(api_key="72x9myrMio2LKMuyWxVR",secret_key="Ywujy3nNLBncuvWxfj9bryNSZpM")
    a=gem.symbols()
    c=gem.price(symbol='btcusd')
    d=gem.new_order(amount="5",price="3528.85",side="buy",client_order_id="3424",symbol='btcusd',type='exchange limit', options=["maker-or-cancel"])
    e=gem.book(symbol='btcusd',limit_asks=0,limit_bids=0)

    anum = int(input("Please enter a number"))


    

if __name__ == "__main__":
    main()



