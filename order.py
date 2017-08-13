
import uuid
from enum import Enum

class OrderType(Enum):
    limit="limit"
    market="market"

class OrderDirection(Enum):
    buy="buy"
    sell="sell"


class Order():

    def __init__(self, direction, type, price, quantity,timeMade):
        if isinstance(type, OrderType):
            self.type=type
        else:
            print("order type is not part of OrderType")
        self.price=price
        self.quantity=quantity
        self.totalprice=price*quantity
        self.id=str(uuid.uuid4())
        self.timeMade=timeMade
        self.timeCompleted=self.timeMade


        
