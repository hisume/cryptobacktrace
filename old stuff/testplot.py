import plotly.plotly as py
import plotly.graph_objs as go
import datetime

# Create random data with numpy
import numpy as np


btime=[]
bprice=[]


time=[]
price=[]
file=open("btc.csv")
i=0
for line in file:
    l=line.rstrip().split(",")
    time.append(datetime.datetime.strptime(l[0],'%Y-%m-%dT%H:%M:%S.%fZ'))
    price.append(l[1])
    if i%2000 ==0:
        btime.append(datetime.datetime.strptime(l[0],'%Y-%m-%dT%H:%M:%S.%fZ'))
        bprice.append(l[1])
    i+=1



# Create traces
trace0 = go.Scatter(
    x = time,
    y = price,
    mode = 'lines',
    name = 'lines'
)

trace1 = go.Scatter(
    x = btime,
    y = bprice,
    mode = 'markers',
    marker = dict(
        size = 10,
        color = 'rgba(0, 190, 0, .8)',
    )
)

data = [trace0,trace1]

layout = dict(
    title='Time series with range slider and selectors',
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
py.plot(fig, filename='line-mode')