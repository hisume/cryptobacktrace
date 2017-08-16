import boto3
import json

class CryptoDB:
    """class that contains dynamo DB access options"""

    def __init__(self):

        with open('.keyaws.json') as data_file:    
            data = json.load(data_file)

        client=boto3.client(
            'dynamodb',
            aws_access_key_id=data['accessKeyId'],
            aws_secret_access_key=data['secretAccessKey'],
            region_name=data['region']
        )
        
        self.tableName="CryptoDB"

    def getDateRangeData(currencyPair, startDate, endDate, callBack):
        """Gets DynamoDB price data from date range from table"""
        
        


a=CryptoDB()