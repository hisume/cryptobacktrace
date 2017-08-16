import datetime
from order import Order, OrderDirection,OrderType
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go

class Simulate:

    def __init__(self, startAmount, data):
        self.cash=startAmount
        if isinstance(data,list):
            self.data=data 
        else:
            raise ValueError("Data must be a list of time,value")
        
        self.frame=0
        self.limitOrders=[]
        self.completedOrders=[]
        self.position=0 #cryptopcurrency quantity
        self.buyPause=0
        self.plotPrice=[]
        self.plotTime=[]
        self.plotBuyTime=[]
        self.plotSellTime=[]
        self.plotBuyPrice=[]
        self.plotSellPrice=[]
        self.marketPrice=0
    
    def executeorder(self, order):
        """processes order This function execute the order market or limit """

        
        if order.type == OrderType.market:
            totalPrice=self.marketPrice*order.quantity
            order.totalPrice=totalPrice
            if order.direction == OrderDirection.buy: #market buy
                if self.cash <=totalPrice: #check if there's enough cash to market buy
                    print("Warning: not enough cash to buy @market {0} at market price ({1}). Cash remaining: ${2}".format(order.quantity, self.marketPrice, self.cash))
                    return -1
                else:
                    self.cash-=totalPrice
                    self.position+=order.quantity
                    print("BOUGHT at {} (Total:{}) on {}".format(order.price, totalPrice, self.frametime.isoformat()))
            else: #market sell
                if self.position < order.quantity: #check if there's enough position to sell
                    print("Warning: not enough position to sell @market {0} at market price ({1}). Position: {2}".format(order.quantity, self.marketPrice, self.position))
                    return -1
                else:
                    self.cash-=totalPrice
                    self.position+=order.quantity
                    print("SOLD at {} (Total:{}) on {}".format(order.price, totalPrice, self.frametime.isoformat()))

            order.timeCompleted=datetime.datetime.now()
            self.completedOrders+=order
        elif order.type == OrderType.limit:
            totalPrice=order.price * order.quantity
            order.totalPrice=totalPrice
            if order.direction == OrderDirection.buy and order.price >= self.marketPrice: #check if buy price is higher than market. If so, then we can buy
                if self.cash <= totalPrice:  # check if there's enough cash to market buy
                    print("Warning: not enough cash to buy @market {0} at market price ({1}). Cash remaining: ${2}".format(order.quantity, self.marketPrice, self.cash))
                    return -1
                else:
                    self.cash-=totalPrice
                    self.position+=order.quantity
                    order.timeCompleted=datetime.datetime.now()
                    self.limitOrders.remove(order)
                    self.completedOrders.append(order)
                    print("BOUGHT at {} (Total:{}) on {}".format(order.price, totalPrice, self.frametime.isoformat()))
                    self.plotBuyPrice.append(order.price)
                    self.plotBuyTime.append(self.frametime)
                    ###STRATEGY CREATE SELL LIMIT ORDER
                    newPrice=order.price*1.01
                    self.limitOrders.append(Order(direction=OrderDirection.sell,type=OrderType.limit,price=newPrice,quantity=0.1,timeMade=self.frametime,oldPrice=order.price))
                    print("Created sell limit order at {} (Total:{}) on {} from previous buy order".format(newPrice, totalPrice, self.frametime.isoformat()))
                

            elif order.direction == OrderDirection.sell and order.price <= self.marketPrice:  #check if sell price is lower than market. If so, then we can sell
                if self.position < order.quantity: #check if there's enough position to sell
                    print("Warning: not enough position to sell @market {0} at market price ({1}). Position: {2}".format(order.quantity, self.marketPrice, self.position))
                    return -1
                else:
                    self.cash+=totalPrice
                    self.position-=order.quantity
                    order.timeCompleted=datetime.datetime.now()
                    self.limitOrders.remove(order)
                    self.completedOrders.append(order)
                    print("SOLD at {} (Total:{}) on {}. Change: {}".format(order.price, totalPrice, self.frametime.isoformat(),totalPrice - order.oldPrice*order.quantity))
                    self.plotSellPrice.append(order.price)
                    self.plotSellTime.append(self.frametime)

            else:
                    print("Error processing limit {} order (check camparison of limit price ({}) to market price ({})".format(order.direction, order.price, self.marketPrice))
        else:
            raise ValueError("Submit order has unknown type: {0}".format(order.type))
        

    def processlimitorderlist(self):
        """This function processes all the limit orders that are in the limit orders list
        by checking if 1. The limit price has been reached. 2. if it has, execute order
        """

        for order in self.limitOrders: #process all the limit orders
            if (order.direction == OrderDirection.buy and order.price >= self.marketPrice) or (order.direction == OrderDirection.sell and order.price <= self.marketPrice): 
                self.executeorder(order)
        
    def getLimitOrders(self, orderType):
        """`gets all orders of OrderDirection type (buy, sell)"""
        temp=[]
        for x in self.limitOrders:
            if x.direction == orderType:
                temp.append(x)
        return temp
        
    def tick(self):
        """processes all actions that needs to be taken this tick"""
        self.frame+=1
        self.frametime=datetime.datetime.strptime(data[self.frame].split(",")[0],'%Y-%m-%dT%H:%M:%S.%fZ')
        self.marketPrice=float(data[self.frame].split(",")[1])

        

        #strategy (self contained for now)
        limitOrderQuantity=20 #if gmva buy % goes up, this should go down. Those two control the pace
        self.buyPauseLimit=10 #frames to wait before another buy
        
        mvaFrameCount=60
        gmvaFrameCount=360 #greater mva (bigger range)
        if self.frame < gmvaFrameCount: #set frame ahead of moving average frame amount in case we just started
            self.frame=gmvaFrameCount
            return
        temp=[]
        for point in data[(self.frame-mvaFrameCount):self.frame]:
            temp.append(float(point.split(",")[1]))
        mva=np.mean(temp)

        for point in data[(self.frame-gmvaFrameCount):self.frame]:
            temp.append(float(point.split(",")[1]))
        gmva=np.mean(temp)

        self.plotPrice.append(self.marketPrice)
        self.plotTime.append(self.frametime)


 #       print("{}. Market Price: {}. MVA: {}".format(sim.frametime, marketPrice,mva))
        self.processlimitorderlist()
        
        #delete all buy orders that lasted for longer than a day
        for o in self.limitOrders:
            if o.direction == OrderDirection.buy and (o.timeMade < self.frametime-datetime.timedelta(hours=8)):
                self.limitOrders.remove(o)

        #for sell orders that are longer than a day, wadjust them to mva+percentage
        for o in self.limitOrders:
            if o.direction == OrderDirection.sell and (o.timeMade < self.frametime-datetime.timedelta(hours=12)):
                newPrice=mva*1.003
                print("Repricing sell order from {} to {} on {}".format(o.price,newPrice, self.frametime.isoformat()))
                o.price=newPrice 
                


        #when to buy
        if len(self.limitOrders) < limitOrderQuantity and self.buyPause < 1:
            if self.marketPrice*1.002 < mva and self.marketPrice*1.0175 > mva and self.marketPrice*1.005 < gmva: #buy if less than average by a %, less than greater average by a %, but when the less is no more than 1.75%
                self.limitOrders.append(Order(direction=OrderDirection.buy,type=OrderType.limit,price=self.marketPrice-1,quantity=0.1,timeMade=self.frametime))
                print("Created buy limit order at {} on {}".format(self.marketPrice-1, self.frametime.isoformat()))
                self.buyPause=self.buyPauseLimit

        self.buyPause-=1
            

    def sellall(self):
        """After we finish, sell out all of our position with price from the last frame"""
        self.cash+=self.position*float(data[-1].split(",")[1])

    def complete(self):
        self.sellall()
        #plot
        pricePlot = go.Scatter(
            x=self.plotTime,
            y=self.plotPrice,
            mode='lines',
            name='Price'
        )

        buyPlot = go.Scatter(
            x=self.plotBuyTime,
            y=self.plotBuyPrice,
            mode='markers',
            marker=dict(
                size=10,
                color='rgba(0, 190, 0, .8)',
            )
        )
        sellPlot = go.Scatter(
            x=self.plotSellTime,
            y=self.plotSellPrice,
            mode='markers',
            marker=dict(
                size=10,
                color='rgba(190, 0, 0, .8)',
            )
        )
        data = [pricePlot,buyPlot,sellPlot]

        layout = dict(
            title='Crypto Simulation',
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label='1m',
                            step='month',
                            stepmode='backward'),
                        dict(count=6,
                            label='6m',
                            step='month',
                            stepmode='backward'),
                        dict(count=1,
                            label='YTD',
                            step='year',
                            stepmode='todate'),
                        dict(count=1,
                            label='1y',
                            step='year',
                            stepmode='backward'),
                        dict(step='all')
                    ])
                ),
                rangeslider=dict(),
                type='date'
            )
        )
        fig = dict(data=data, layout=layout)
        py.plot(fig, filename='crypto-simulation')




data=[]
file=open("btc.csv")
for line in file:
    data.append(line.rstrip())

sim=Simulate(startAmount=10000,data=data)

while sim.frame < (len(data)-1):
    sim.tick()

sim.complete()
print("End Money:{}".format(sim.cash))
print("finished")




