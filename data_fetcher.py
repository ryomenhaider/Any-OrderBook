import requests
import json


def fetch_orderboook(symbol:str, limit:int = 20):
    
    res = requests.get(f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit={limit}')
    
