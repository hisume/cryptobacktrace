
import uuid
import enum

class OrderType(Enum):
    limit="limit"
    market="market"

class OrderDirection(Enum):
    buy="buy"
    sell="sell"


class Order():

    def __init__(self, direction, type, price, quantity):
        if isinstance(type, OrderType):
            self.type=type
        else:
            print("order type is not part of OrderType")
        self.price=price
        self.quantity=quantity
        self.totalprice=price*quantity
        self.id=str(uuid.uuid4())
        self.timeMade=datetime.datetime.now()
        self.timeCompleted=self.timeMade


        
