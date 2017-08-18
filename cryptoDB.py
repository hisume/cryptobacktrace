import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import datetime

class CryptoDB:
    """class that contains dynamo DB access options"""

    def __init__(self, tableName="cryptoDB"):

        with open('.keyaws.json') as data_file:    
            data = json.load(data_file)

        self.client=boto3.client(
            'dynamodb',
            aws_access_key_id=data['accessKeyId'],
            aws_secret_access_key=data['secretAccessKey'],
            region_name=data['region']
        )
        
        self.tableName=tableName

    def getDateRangeData(self, currencyPair, startDate, endDate):
        """Gets DynamoDB price data from date range from table"""
        result=[]
        try:
            response=self.client.query(
                TableName=self.tableName,
                ExpressionAttributeNames={"#t": "time", "#cp":"currencyPair"},
                ExpressionAttributeValues= {
                    ":startDate": {'S': startDate}, 
                    ":endDate": {'S': endDate}, 
                    ":cp" : {'S': currencyPair}
                },
                KeyConditionExpression="#cp = :cp and #t between :startDate and :endDate"
            )
            for i in response[u'Items']:
                result.append(i["time"]["S"]+","+i["value"]["N"])

        except Exception as inst:
            print("Error getting data based on time range")
            print(inst)

        return result

    def insertKey(self, currencyPair, date, price):
        pass
    

a=CryptoDB()
data=a.getDateRangeData("BTC-USD", "2017-08-11T23:10:38.486348", '2017-08-16T23:24:27.271083')