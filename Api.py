# fraud_detection_api.py
from fastapi import FastAPI, WebSocket
from pymongo import MongoClient
import redis
import json
import asyncio

# Connect to Redis and MongoDB
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["trading_db"]
fraud_collection = db["fraud_transactions"]

app = FastAPI()

# REST API - Get all fraudulent trades
@app.get("/fraudulent-trades")
def get_fraudulent_trades():
    return list(fraud_collection.find({}, {"_id": 0}))

# REST API - Get fraudulent trades by user ID
@app.get("/fraudulent-trades/{user_id}")
def get_fraudulent_trades_by_user(user_id: str):
    return list(fraud_collection.find({"user_id": user_id}, {"_id": 0}))

# REST API - Delete (mark reviewed) fraudulent trade
@app.delete("/fraudulent-trades/{trade_id}")
def delete_fraudulent_trade(trade_id: str):
    fraud_collection.delete_one({"trade_id": trade_id})
    return {"message": "Fraudulent trade marked as reviewed"}

# WebSocket - Fraud alert streaming
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    pubsub.subscribe("fraud_alerts")
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_text(message["data"])
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
