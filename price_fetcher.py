# price_fetcher/price_fetcher.py

import requests

def get_top_50_crypto_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        result = []
        for coin in data:
            result.append({
                "id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "price": coin["current_price"],
                "price_change_24h": coin["price_change_percentage_24h"],
                "volume": coin["total_volume"]
            })

        return result

    except Exception as e:
        print("Error fetching crypto prices:", e)
        return []