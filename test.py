import requests, json

def fetch_kline():

    url = f'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=60'
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            print(json.dumps(data))
            

    except Exception as e:
        raise ConnectionError(f"the status code is {e}")
    
fetch_kline()