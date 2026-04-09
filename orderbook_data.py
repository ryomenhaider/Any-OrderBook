import requests
import json


def fetch_orderboook(symbol: str, limit: int = 20):

    url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit={limit}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            return symbol, data

    except Exception as e:
        raise ConnectionError(f"the status code is {e}")


def clean_orderbook(data):

    bids = [{"price": float(b[0]), "quantity": float(b[1])} for b in data["bids"]]
    asks = [{"price": float(a[0]), "quantity": float(a[1])} for a in data["asks"]]

    return bids, asks


def feature_engineer(bids, asks):

    def spread():
        max_bid = max(bids, key=lambda x: x["price"])
        min_ask = min(asks, key=lambda x: x["price"])
        spread_val = min_ask["price"] - max_bid["price"]
        spread_pct = (spread_val / min_ask["price"]) * 100
        mid_price = (max_bid["price"] + min_ask["price"]) / 2
        return spread_val, spread_pct, mid_price

    def depth():
        bid_depth = sum(b["quantity"] for b in bids)
        ask_depth = sum(a["quantity"] for a in asks)
        return bid_depth, ask_depth

    def imbalance_ratio():
        bid_depth, ask_depth = depth()
        return bid_depth / (bid_depth + ask_depth)

    def vwap():
        def bid_vwap():
            total_value = sum(b["price"] * b["quantity"] for b in bids)
            total_qty = sum(b["quantity"] for b in bids)
            return total_value / total_qty

        def ask_vwap():
            total_value = sum(a["price"] * a["quantity"] for a in asks)
            total_qty = sum(a["quantity"] for a in asks)
            return total_value / total_qty

        return bid_vwap(), ask_vwap()

    return {
        "spread": spread(),
        "depth": depth(),
        "imbalance_ratio": imbalance_ratio(),
        "vwap": vwap(),
    }
