# redis_stream_simulation.py
import redis
import json
import random
import uuid
from datetime import datetime, timezone
import time

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Generate a random trade event
def generate_trade():
    user_id = f"U{random.randint(1000, 9999)}"
    trade_id = f"T{uuid.uuid4().hex[:8]}"
    stock_symbol = random.choice(["AAPL", "GOOG", "TSLA", "AMZN", "MSFT"])
    trade_type = random.choice(["BUY", "SELL"])
    quantity = random.randint(1, 1000)
    price_per_unit = round(random.uniform(100, 1000), 2)
    timestamp = datetime.now(timezone.utc).isoformat() + "Z"
    location = random.choice(["New York, USA", "London, UK", "Tokyo, Japan", "Berlin, Germany"])
    ip_address = f"192.168.1.{random.randint(1, 255)}"

    return {
        "user_id": user_id,
        "trade_id": trade_id,
        "stock_symbol": stock_symbol,
        "trade_type": trade_type,
        "quantity": quantity,
        "price_per_unit": price_per_unit,
        "timestamp": timestamp,
        "location": location,
        "ip_address": ip_address
    }

# Simulate trades and push to Redis
while True:
    trade = generate_trade()
    redis_client.xadd("trade_stream", trade, maxlen=1000)
    time.sleep(random.uniform(0.5, 2))  # Randomized trade intervals
