import json
import os
from datetime import datetime, timedelta
from mexc_client import MexcClient
from dotenv import load_dotenv

load_dotenv()

def to_ms_timestamp(dt: datetime) -> int:
    """Converts a datetime object to a millisecond timestamp."""
    return int(dt.timestamp() * 1000)

def pretty_print(data):
    """Prints data in a readable JSON format."""
    if data is not None:
        print(json.dumps(data, indent=4))
    else:
        print("No data received or an error occurred.")

# --- Configuration ---
API_KEY = os.environ.get("MEXC_API_KEY", "your_api_key")
SECRET_KEY = os.environ.get("MEXC_API_SECRET", "your_api_secret")


# --- Initialize Client ---
client = MexcClient(api_key=API_KEY, secret_key=SECRET_KEY)

# --- Define Time Range for 90-day History ---
now = datetime.now()
end_date = now
start_date_90_days = now - timedelta(days=90)


# --- Fetch Deposit History for the last 90 days ---
print("--- 💰 Fetching Deposit History for BTC for the last 90 days... ---")
ninety_day_deposits = client.fetch_historical_data(
    fetch_function=client.get_deposit_history,
    max_days_per_request=7,
    start_date=start_date_90_days,
    end_date=end_date,
    coin="BTC"
)
print(f"\n--- ✅ Found a total of {len(ninety_day_deposits)} BTC deposits in the last 90 days. ---")
pretty_print(ninety_day_deposits)
print("-" * 50)

# --- Fetch Withdrawal History for the last 90 days ---
print("\n--- 💸 Fetching Withdrawal History for USDC for the last 90 days... ---")
ninety_day_withdrawals = client.fetch_historical_data(
    fetch_function=client.get_withdrawal_history,
    max_days_per_request=7,
    start_date=start_date_90_days,
    end_date=end_date,
    coin="USDC"
)
print(f"\n--- ✅ Found a total of {len(ninety_day_withdrawals)} USDC withdrawals in the last 90 days. ---")
pretty_print(ninety_day_withdrawals)
print("-" * 50)

# --- Fetch recent orders ---
print("\n--- 📈 Fetching recent orders for BTCUSDC... ---")
# Define a shorter time range for orders, e.g., last 24 hours
start_date_orders = now - timedelta(days=6)
recent_orders = client.get_all_orders(
    symbol="BTCUSDC",
    start_time=to_ms_timestamp(start_date_orders),
    end_time=to_ms_timestamp(end_date)
)

if recent_orders:
    print(f"\n--- ✅ Found a total of {len(recent_orders)} orders for BTCUSDC in the last day. ---")
    # Filter for completed orders ('FILLED')
    completed_orders = [order for order in recent_orders if order.get('status') == 'FILLED']
    print(f"---    ({len(completed_orders)} of them are completed) ---")
    pretty_print(completed_orders)
else:
    print("\n--- ⚠️ No orders found or an error occurred. ---")

print("-" * 50)

print("\n--- 📈 Fetching recent orders for DOGEUSDT... ---")
# Define a shorter time range for orders, e.g., last 24 hours
start_date_orders = now - timedelta(days=6)
recent_orders = client.get_all_orders(
    symbol="DOGEUSDT",
    start_time=to_ms_timestamp(start_date_orders),
    end_time=to_ms_timestamp(end_date)
)

if recent_orders:
    print(f"\n--- ✅ Found a total of {len(recent_orders)} orders for DOGEUSDT in the last day. ---")
    # Filter for completed orders ('FILLED')
    completed_orders = [order for order in recent_orders if order.get('status') == 'FILLED']
    print(f"---    ({len(completed_orders)} of them are completed) ---")
    pretty_print(completed_orders)
else:
    print("\n--- ⚠️ No orders found or an error occurred. ---")

print("-" * 50)

