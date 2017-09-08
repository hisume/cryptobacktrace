import time
import random
import datetime
 
#lines=int(input("how many lines would you like to generate?"))
lines = 100
currentPrice = 110
modRange =10
result = []
tick = datetime.datetime.now()
fileName="testdata.txt"
 
def modprice(currentPrice):
    rand=random.randint(0,modRange)
    if rand%2: #if its odd, then subtract stuff
        currentPrice= currentPrice+rand
    else:
        currentPrice= currentPrice-rand
    return currentPrice
 
for x in range(0, lines):
    tick = tick-datetime.timedelta(minutes=5)
    result.append(tick.isoformat()+","+str(modprice(currentPrice))+'\r\n')
 
with open(fileName, 'w') as fs:
    fs.writelines(result)

    