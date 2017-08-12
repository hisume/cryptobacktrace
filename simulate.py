import datetime
from order import Order, OrderDirection,OrderType


class simulate():

    def __init_(self, startAmount, data):
        self.reserve=startAmount
        if isinstance(a,list):
            self.data=data
        else:
            raise ValueError("Data must be a list of time,value")
        
        self.frame=0
        self.limitOrders=[]
        self.completedOrders[]
    
    def submitOrder(self, order):
        """processes order"""
        if order.direction == OrderDirection.buy:
            if order.type == OrderType.market:
                priceAmount=int(data[0].split(",")[1])*order.quantity
                self.cash-=priceAmount
                order.totalPrice=priceAmount
                order.timeCompleted=datetime.datetime.now()
                self.completedOrders+=order
            elif order.type == OrderType.limit:
                self.limitOrders+=order
        else:


    def tick(self):


        self.data.pop()


