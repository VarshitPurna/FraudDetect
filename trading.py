# fraud_detection.py
import redis
import json
import time
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from sklearn.ensemble import IsolationForest
import random

# Connect to Redis and MongoDB
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["trading_db"]
fraud_collection = db["fraud_transactions"]

# Train Machine Learning Model for Anomaly Detection
def train_model():
    # Simulating data for training (you should use actual trade data in production)
    trades = [{"quantity": random.randint(1, 1000), "price_per_unit": random.uniform(100, 1000)} for _ in range(100)]
    X = [[trade["quantity"], trade["price_per_unit"]] for trade in trades]
    model = IsolationForest(n_estimators=100, contamination=0.1)
    model.fit(X)
    return model

# Fraud detection logic
user_trades = {}
model = train_model()

from bson import ObjectId

# Helper function to recursively convert ObjectId to string
def convert_objectid_to_str(obj):
    if isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj

from bson import ObjectId, json_util

# Helper function to convert ObjectId to string
def convert_objectid_to_str(obj):
    if isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj

def detect_fraud(trade):
    user_id = trade["user_id"]
    timestamp = datetime.fromisoformat(trade["timestamp"].replace("Z", ""))

    if user_id not in user_trades:
        user_trades[user_id] = []

    user_trades[user_id].append(trade)
    user_trades[user_id] = [t for t in user_trades[user_id] if datetime.fromisoformat(t["timestamp"].replace("Z", "")) > timestamp - timedelta(seconds=5)]

    fraud_reason = None

    # High-frequency trading
    if len(user_trades[user_id]) >= 5:
        fraud_reason = "High Frequency"

    # Unusual trade size
    avg_quantity = sum(int(t["quantity"]) for t in user_trades[user_id]) / len(user_trades[user_id])  # Convert to integer
    if int(trade["quantity"]) > 10 * avg_quantity:
        fraud_reason = "Unusual Trade Size"

    # Spoofing detection
    buy_sell_times = {t["trade_type"]: datetime.fromisoformat(t["timestamp"].replace("Z", "")) for t in user_trades[user_id]}
    if "BUY" in buy_sell_times and "SELL" in buy_sell_times:
        if abs((buy_sell_times["BUY"] - buy_sell_times["SELL"]).total_seconds()) < 2:
            fraud_reason = "Spoofing"

    # Geographic anomaly
    locations = {t["location"] for t in user_trades[user_id]}
    if len(locations) > 1:
        fraud_reason = "Geographic Anomaly"

    if fraud_reason:
        fraud_entry = {
            "user_id": trade["user_id"],
            "trade_id": trade["trade_id"],
            "stock_symbol": trade["stock_symbol"],
            "reason": fraud_reason,
            "trade_details": trade,
            "created_at": datetime.now(timezone.utc).isoformat()  # Using timezone-aware UTC time
        }

        # Convert any ObjectId to string
        fraud_entry = convert_objectid_to_str(fraud_entry)

        # Insert the entry into MongoDB
        fraud_collection.insert_one(fraud_entry)  # MongoDB will generate a unique _id if not provided

        # Publish to Redis using bson.json_util.dumps, which handles ObjectId correctly
        redis_client.publish("fraud_alerts", json_util.dumps(fraud_entry))  # Publish to Redis

while True:
    trade_data = redis_client.xread({"trade_stream": "0"}, block=0)
    for trade_data_entry in trade_data:
        trade = trade_data_entry[1][0][1]
        detect_fraud(trade)
    time.sleep(1)
