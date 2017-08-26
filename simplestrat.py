import datetime
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go

class SimpleStrat:

    def __init__(self, broker):
        self.broker=broker

        self.max_frames_required=360
        self.mva_frame_count=60
        self.gmva_frame_count=360
        self.mva=0
        self.gmva=0

        self.tick_time=1 #frame frequency by minute
        self.ticks_between_buys=10
        self.ticks_between_buys_count=0
  

        self.buy_order_expiration=datetime.timedelta(hours=8) #buy order expiration time
        self.sell_order_expiration=datetime.timedelta(hours=16) #buy order expiration time
        self.sell_order_expiration_reprice_ratio=1.01 #mva ratio to reprice expired sell orders

        self.resell_price_ratio=1.025 #resell ratio for creating sell order after buy limit order fulfilled

        self.max_orders=20


        self.plot_price= []
        self.plot_time=[]
        self.plot_buy_time=[]
        self.plot_sell_time=[]
        self.plot_buy_price=[]
        self.plot_sell_price=[]
        self.plot_cash=[] #cash on hand
        self.plot_value=[] #total value of cash + position
        self.plot_mva=[]


    def tick(self):
        #calculate MVA
        temp= []
        for point in self.broker.data[(len(self.broker.data)-self.mva_frame_count):(len(self.broker.data)-1)]:
            temp.append(float(point.split(",")[1]))
        self.mva= np.mean(temp)

        for point in self.broker.data[(len(self.broker.data)-self.gmva_frame_count):(len(self.broker.data)-1)]:
            temp.append(float(point.split(",")[1]))
        self.mva= np.mean(temp)

        self.plot_price.append(self.broker.market_price)
        self.plot_time.append(self.broker.frame_time)
        self.plot_mva.append(self.mva)
        print("{}   price: {}    mva: {}".format(self.broker.frame_time.isoformat(), self.broker.market_price, self.mva))
        
        #delete buy orders that last for longer than a certain time
        for o in self.broker.limit_orders:
            if o['side'] == 'buy' and (o['created_at'] < (self.broker.frame_time-self.buy_order_expiration).isoformat()):
                self.broker.cancel_order(o['id'])
                print("Canceling buy order of {} on {}".format(o['price'],self.broker.frame_time.isoformat()))

        #reprice sell orders that last longer than a certain time
        for o in self.broker.limit_orders:
            if o['side'] == 'sell' and (o['created_at'] < (self.broker.frame_time-self.sell_order_expiration).isoformat()):
                
                ret=self.broker.cancel_order(o['id'])
                #make sure the order is canceled before doing another buy order
                if ret[0] == o.id:
                    new_price=self.mva*self.sell_order_expiration_reprice_ratio
                    print("Repricing sell order from {} to {} on {}".format(o['price'],new_price, self.broker.frame_time.isoformat()))
                    self.broker.create_order(limit_price=new_price, amount=o['size'], direction='buy')
                    


        #Create buy orders
        if len(self.broker.limit_orders) < self.max_orders and self.ticks_between_buys_count > self.ticks_between_buys:
            if self.broker.market_price < self.mva*.998 and self.broker.market_price > self.mva*.975 and self.broker.market_price > self.gmva*0.96: #buy if less than average by a %, less than greater average by a %, but when the less is no more than 1.75%
                new_price=self.broker.market_price - 0.01
                print("Created buy limit order at {} on {}".format(new_price, self.broker.frame_time.isoformat()))
                order=self.broker.create_order(limit_price=new_price, amount=0.01, direction='buy')
                if order != 0:

                    self.ticks_between_buys_count=0
                    self.plot_buy_price.append(new_price)
                    self.plot_buy_time.append(self.broker.frame_time)
                else:
                    print("Error Creating buy order on {}. Message: {}".format(self.broker.frame_time.isoformat(), order['message']))


        #If a buy order is completed, then make a sell order
        for o in self.broker.completed_orders:
            self.broker.completed_orders+=o
            if o.side == 'buy':
                self.plot_buy_price.append(o['price'])
                self.plot_buy_time.append(self.broker.frame_time.isoformat())
                #create sell order
                new_price=o['price']*self.resell_price_ratio
                order=self.broker.create_order(limit_price=new_price, amount=o['size'], direction='buy')
                if order != 0:
                    print("Created reselling buy limit order at {} on {}".format(new_price, self.broker.frame_time.isoformat()))
            if o.side == 'sell':
                print("SOLD at {} (Total:{}) on {}.".format(o['price'], (o['size']*o['price']),self.broker.frame_time.isoformat()))   
                self.plot_sell_price.append(o['price'])
                self.plot_sell_time.append(self.broker.frame_time.isoformat())


        self.ticks_between_buys_count+=1
        self.plot_cash.append(self.broker.cash)
        self.plot_value.append(self.broker.get_account_value())
                
                

    def plot(self):
        pricePlot = go.Scatter(
            x=self.plot_time,
            y=self.plot_price,
            mode='lines',
            name='Price'
        )
        mvaPlot = go.Scatter(
            x=self.plot_time, 
            y=self.plot_mva,
            mode='lines',
            name='MVA'
        )


        buyPlot = go.Scatter(
            x=self.plot_buy_time,
            y=self.plot_buy_price,
            mode='markers',
            name="Buy",
            marker=dict(
                size=10,
                color='rgba(0, 190, 0, .8)',
            )
        )
        sellPlot = go.Scatter(
            x=self.plot_sell_time,
            y=self.plot_sell_price,
            mode='markers',
            name="Sell",
            marker=dict(
                size=10,
                color='rgba(190, 0, 0, .8)',
            )
        )
        cashPlot = go.Scatter(
            x=self.plot_time,
            y=self.plot_cash,
            mode='lines',
            name="Cash",
            marker=dict(
                size=10,
                color='rgba(190, 0, 0, .8)',
            ),
            xaxis='x2',
            yaxis='y2'
        )
        valuePlot = go.Scatter(
            x=self.plot_time,
            y=self.plot_value,
            mode='lines',
            name="Total Value",
            marker=dict(
                size=10,
                color='rgba(0, 0, 190, .8)',
            ),
            xaxis='x2',
            yaxis='y2'
        )        
        data = [pricePlot, mvaPlot, buyPlot,sellPlot, cashPlot,valuePlot]

        layout = dict(
            title='Crypto Simulation',
            xaxis=dict(
                rangeslider=dict(),
                type='date',
                domain=[0,1]
            ),
            yaxis=dict(
                domain=[0,0.8]
            ),
            xaxis2=dict(
                domain=[0,1],
                anchor='y2'
            ),
            yaxis2=dict(
                domain=[0.8,1],
                anchor='x2'
            )

        )
        fig = dict(data=data, layout=layout)
        py.plot(fig, filename='crypto-stuff')      





