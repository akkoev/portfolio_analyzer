import requests
import datetime
import hmac
import hashlib
import time
from urllib.parse import urlencode
from datetime import datetime, timedelta

class MexcClient:
    """
    A simple client for interacting with the MEXC API (V3).
    """
    BASE_URL = "https://api.mexc.com"

    def __init__(self, api_key: str, secret_key: str):
        """
        Initializes the MexcClient.

        Args:
            api_key (str): Your MEXC API key.
            secret_key (str): Your MEXC secret key.
        """
        if not api_key or not secret_key:
            raise ValueError("API key and secret key cannot be empty.")
        self.api_key = api_key
        self.secret_key = secret_key
        self.headers = {
            "X-MEXC-APIKEY": self.api_key,
            "Content-Type": "application/json"
        }

    def _generate_signature(self, params: dict) -> str:
        """
        Generates the HMAC SHA256 signature for the request.

        Args:
            params (dict): A dictionary of query parameters.

        Returns:
            str: The lowercase hexadecimal signature.
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _send_request(self, method: str, endpoint: str, params: dict = None):
        """
        Sends an authenticated request to the MEXC API.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST').
            endpoint (str): API endpoint path (e.g., '/api/v3/account').
            params (dict, optional): Request parameters. Defaults to None.

        Returns:
            dict: The JSON response from the API.
        """
        if params is None:
            params = {}
            
        # Add timestamp to all requests
        params['timestamp'] = int(time.time() * 1000)
        
        # Sort parameters alphabetically for consistent signature generation
        sorted_params = dict(sorted(params.items()))

        # Generate and add signature
        signature = self._generate_signature(sorted_params)
        sorted_params['signature'] = signature

        url = f"{self.BASE_URL}{endpoint}?{urlencode(sorted_params)}"
        
        try:
            response = requests.request(method, url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - {response.text}")
        except Exception as err:
            print(f"An other error occurred: {err}")
        return None

    def fetch_historical_data(self, fetch_function, max_days_per_request: int, start_date: datetime, end_date: datetime, **kwargs):
        """
        Fetches data in chunks when an API endpoint has a date range limit.
        """
        all_results = []
        current_start = start_date
        
        print(f"Fetching historical data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
        print(f"API Limit: {max_days_per_request} days per request.")

        while current_start < end_date:
            chunk_end = min(current_start + timedelta(days=max_days_per_request), end_date)
            
            print(f"  > Fetching chunk: {current_start.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}")

            start_ts = int(current_start.timestamp() * 1000)
            end_ts = int(chunk_end.timestamp() * 1000)

            response_data = fetch_function(
                start_time=start_ts,
                end_time=end_ts,
                **kwargs
            )

            if response_data:
                if isinstance(response_data, list):
                    all_results.extend(response_data)
                elif 'rows' in response_data and isinstance(response_data.get('rows'), list):
                     all_results.extend(response_data['rows'])
                else:
                    print(f"  > Warning: Received data in an unexpected format: {response_data}")

            current_start += timedelta(days=max_days_per_request)
            time.sleep(0.5) 

        return all_results

    def get_deposit_history(self, coin: str = None, start_time: int = None, end_time: int = None):
        """
        Fetches the deposit history. API limit is 7 days per request.
        """
        endpoint = "/api/v3/capital/deposit/hisrec"
        params = {}
        if coin:
            params['coin'] = coin
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
            
        return self._send_request('GET', endpoint, params)

    def get_withdrawal_history(self, coin: str = None, start_time: int = None, end_time: int = None):
        """
        Fetches the withdrawal history. API limit is 7 days per request.
        """
        endpoint = "/api/v3/capital/withdraw/history"
        params = {}
        if coin:
            params['coin'] = coin
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
            
        return self._send_request('GET', endpoint, params)

    def get_universal_transfer_history(self, start_time: int = None, end_time: int = None, from_account_type: str = None, to_account_type: str = None):
        """
        Fetches the universal transfer history between main and sub-accounts.
        """
        endpoint = "/api/v3/capital/sub-account/universalTransfer"
        params = {}
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        if from_account_type:
            params['fromAccountType'] = from_account_type
        if to_account_type:
            params['toAccountType'] = to_account_type

        return self._send_request('GET', endpoint, params)

    def get_sub_account_assets(self, sub_account: str, account_type: str = "SPOT"):
        """
        Fetches the asset details for a specific sub-account.
        """
        endpoint = "/api/v3/sub-account/asset"
        params = {'subAccount': sub_account, 'accountType': account_type}
        return self._send_request('GET', endpoint, params)

    def get_all_orders(self, symbol: str, start_time: int = None, end_time: int = None, limit: int = 1000):
        """
        Fetches all orders for a specific symbol.

        Args:
            symbol (str): The trading symbol (e.g., 'BTCUSDT').
            start_time (int, optional): Start time in milliseconds timestamp.
            end_time (int, optional): End time in milliseconds timestamp.
            limit (int, optional): The number of orders to return (default 500, max 1000).

        Returns:
            list: A list of orders.
        """
        endpoint = "/api/v3/allOrders"
        params = {'symbol': symbol, 'limit': limit}
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
            
        return self._send_request('GET', endpoint, params)
