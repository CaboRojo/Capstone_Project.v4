import requests
import logging
from datetime import datetime, timedelta

class AlphaVantageAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query?"

    def make_request(self, params):
        params['apikey'] = self.api_key  # Ensure API key is included in all requests
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error("Request exception: %s", e)
            return None

    def get_stock_final_price(self, symbol):
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact'
        }
        data = self.make_request(params)
        if data and 'Time Series (Daily)' in data:
            latest_date = max(data['Time Series (Daily)'].keys())
            return float(data['Time Series (Daily)'][latest_date]["4. close"])
        return None

    def get_historical_stock_prices(self, symbol):
        """Fetch historical stock prices for the last year."""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'full'
        }
        data = self.make_request(params)
        if data and 'Time Series (Daily)' in data:
            one_year_ago = datetime.now() - timedelta(days=365)
            one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')
            
            historical_prices = {date: info["4. close"] for date, info in data['Time Series (Daily)'].items() if date >= one_year_ago_str}
            return historical_prices
        return None