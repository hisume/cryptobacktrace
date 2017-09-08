# Cryptobacktrace

This library does back trading to test out trading strategies for data stored in a list format of "datetime_in_iso_format","value_of_currency"

The main class broker.py which performs common functions such as creating a buy order or getting recently filled orders based on the data. For example, if you made a buy order at $3000 for BTC, and the next data frame (say, 1 minute later) has the price at $2999, it will execute that buy order.

You can plug in Strategies to the broker, which does all the logic around when to buy and when to sell. Strategies can also plot to make it easier to fine-tune your strategy's numbers.

