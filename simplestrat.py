import datetime
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

        self.tick_time=datetime.timedelta(minutes=1) #frame frequency by minute
        self.ticks_between_buys=10
        self.ticks_between_buys_count=0
  

        self.buy_order_expiration=datetime.timedelta(hours=8) #buy order expiration time
        self.sell_order_expiration=datetime.timedelta(hours=16) #buy order expiration time
        self.sell_order_expiration_reprice_ratio=1.01 #mva ratio to reprice expired sell orders

        self.resell_price_ratio=1.025 #resell ratio for creating sell order after buy limit order fulfilled
        self.buy_amount=0.01
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
        self.ticks_per_plot=15


    def tick(self):
        #calculate MVA
        self.mva= self.broker.get_mva(self.mva_frame_count)
        self.gmva= self.broker.get_mva(self.gmva_frame_count)

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
                new_price=self.broker.market_price - 0.02
                print("Created buy limit order at {} on {}".format(new_price, self.broker.frame_time.isoformat()))
                order=self.broker.create_order(limit_price=new_price, amount=self.buy_amount, direction='buy')
                if order != 0:

                    self.ticks_between_buys_count=0
                    self.plot_buy_price.append(new_price)
                    self.plot_buy_time.append(self.broker.frame_time)
                else:
                    print("Error Creating buy order on {}. Message: {}".format(self.broker.frame_time.isoformat(), order['message']))


        #If a buy order is completed, then make a sell order from average price of all completed orders


        for o in self.broker.recently_filled_orders:
            self.broker.completed_orders+=o
            bought_total=0.0 #cash spent buying (position bought *price)
            bought_position=0.0   #amount of crypto bought
            sold_total= 0.0
            sold_position= 0.0

            if o.side == 'buy':
                bought_position+=float(o['size'])
                bought_total+=(float(o['size'])* float(o['price']))
            if o.side == 'sell':
                sold_position+=float(o['size'])
                sold_total+=(float(o['size'])* float(o['price'])) 

            if bought_total > 0.0:
                avg_price=bought_total/bought_position
                self.plot_buy_price.append(avg_price)
                self.plot_buy_time.append(self.broker.frame_time.isoformat())
                #create sell order
                new_price=avg_price*self.resell_price_ratio
                order=self.broker.create_order(limit_price=new_price, amount=bought_position, direction='sell')
                if order != 0:
                    print("Created reselling buy limit order at {}. (Total: {}) on {}".format(new_price, 
                        new_price*bought_position, self.broker.frame_time.isoformat()))         
            
            if sold_total >0.0:
                avg_price=sold_total/sold_position
                print("SOLD at {} (Total:{}) on {}.".format(avg_price, (avg_price*sold_position),self.broker.frame_time.isoformat()))   
                self.plot_sell_price.append(avg_price)
                self.plot_sell_time.append(self.broker.frame_time.isoformat())


        self.ticks_between_buys_count+=1
        self.plot_cash.append(self.broker.cash)
        self.plot_value.append(self.broker.get_account_value())


        #plot every so often
        if self.ticks_per_plot < 1:
            self.plot()
        else:
            self.ticks_per_plot-=1
                
                

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





