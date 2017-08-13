import datetime
from order import Order, OrderDirection,OrderType
import numpy as np


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
    
    def executeorder(self, order):
        """processes order This function execute the order market or limit """

        marketPrice=float(data[self.frame].split(",")[1])
        if order.type == OrderType.market:
            totalPrice=marketPrice*order.quantity
            order.totalPrice=totalPrice
            if order.direction == OrderDirection.buy: #market buy
                if self.cash <=totalPrice: #check if there's enough cash to market buy
                    printf("Warning: not enough cash to buy @market {0} at market price ({1}). Cash remaining: ${2}".format(order.quantity, marketPrice, self.cash))
                    return -1
                else:
                    self.cash-=totalPrice
                    self.position+=order.quantity
                    printf("BOUGHT at {} (Total:{}) on {}".format(order.price, totalPrice, self.frametime.now()))
            else: #market sell
                if self.position < order.quantity: #check if there's enough position to sell
                    printf("Warning: not enough position to sell @market {0} at market price ({1}). Position: {2}".format(order.quantity, marketPrice, self.position))
                    return -1
                else:
                    self.cash-=totalPrice
                    self.position+=order.quantity
                    printf("SOLD at {} (Total:{}) on {}".format(order.price, totalPrice, self.frametime.now()))

            order.timeCompleted=datetime.datetime.now()
            self.completedOrders+=order
        elif order.type == OrderType.limit:
            totalPrice=order.price * order.quantity
            order.totalPrice=totalPrice
            if order.direction == OrderDirection.buy and order.price >= marketPrice: #check if buy price is higher than market. If so, then we can buy
                if self.cash <= totalPrice:  # check if there's enough cash to market buy
                    printf("Warning: not enough cash to buy @market {0} at market price ({1}). Cash remaining: ${2}".format(order.quantity, marketPrice, self.cash))
                    return -1
                else:
                    self.cash-=totalPrice
                    self.position+=order.quantity
                    order.timeCompleted=datetime.datetime.now()
                    self.completedOrders.append(self.limitOrders.pop(order))
                    printf("BOUGHT at {} (Total:{}) on {}".format(order.price, totalPrice, self.frametime.now()))
                    ###STRATEGY CREATE SELL LIMIT ORDER
                    newPrice=order.price+(order.price*.08)
                    self.limitOrders.append(Order(direction=OrderDirection.sell,type=OrderType.limit,price=newPrice,quantity=0.1,timeMade=self.frametime))
                    printf("Created sell limit order at {} (Total:{}) on {} from previous buy order".format(newPrice, totalPrice, self.frametime.now()))
                

            elif order.direction == OrderDirection.sell and order.price <= marketPrice:  #check if sell price is lower than market. If so, then we can sell
                if self.position < order.quantity: #check if there's enough position to sell
                    printf("Warning: not enough position to sell @market {0} at market price ({1}). Position: {2}".format(order.quantity, marketPrice, self.position))
                    return -1
                else:
                    self.cash-=totalPrice
                    self.position+=order.quantity
                    order.timeCompleted=datetime.datetime.now()
                    self.completedOrders.append(self.limitOrders.pop(order))
                    printf("SOLD at {} (Total:{}) on {}".format(order.price, totalPrice, self.frametime.now()))
            else:
                    printf("Error processing limit {} order (check camparison of limit price ({}) to market price ({})".format(order.direction, order.price, marketPrice))
        else:
            raise ValueError("Submit order has unknown type: {0}".format(order.type))
        

    def processlimitorderlist(self):
        """This function processes all the limit orders that are in the limit orders list
        by checking if 1. The limit price has been reached. 2. if it has, execute order
        """

        marketPrice=float(data[self.frame].split(",")[1])
        for order in self.limitOrders: #process all the limit orders
            if (order.direction == OrderDirection.buy and order.price >= marketPrice) or (order.direction == OrderDirection.sell and order.price <= marketPrice): 
                executeorder(order)
        
    def tick(self):
        """processes all actions that needs to be taken this tick"""
        self.frame+=1
        self.frametime=datetime.datetime.strptime(data[self.frame].split(",")[0],'%Y-%m-%dT%H:%M:%S.%fZ')
        marketPrice=float(data[self.frame].split(",")[1])

        #strategy (self contained for now)
        limitOrderQuantity=10
        mvaFrameCount=60
        if self.frame < mvaFrameCount: #set frame ahead of moving average frame amount in case we just started
            self.frame=mvaFrameCount
            return
        temp=[]
        for point in data[(self.frame-mvaFrameCount):self.frame]:
            temp.append(float(point.split(",")[1]))

        mva=np.mean(temp)

        #delete all buy orders that lasted for longer than a day
        for o in self.limitOrders:
            if o.timeMade < self.frametime-datetime.timedelta(days=1):
                self.limitOrders.pop(o)

        #when to buy
        if len(self.limitOrders) <= limitOrderQuantity:
            if marketPrice*1.005 < mva: #buy if less than average by 0.5%
                self.limitOrders.append(Order(direction=OrderDirection.buy,type=OrderType.limit,price=marketPrice-1,quantity=0.1,timeMade=self.frametime))
                printf("Created limit order at {} on {}".format(marketPrice-1, self.frametime.now()))
            

    def sellall(self):
        """After we finish, sell out all of our position with price from the last frame"""
        self.cash=self.position*float(data[-1].split(",")[1])

data=[]
file=open("btc.csv")
for line in file:
    data.append(line.rstrip())

sim=Simulate(startAmount=10000,data=data)

while sim.frame < len(data):
    sim.tick()


printf("finished")




