Install Required Dependencies, install the necessary Python libraries using 
install fastapi uvicorn redis pymongo scikit-learn 

Start Redis and MongoDB, ensure both services are running. Start Redis: If Redis is installed, start it using: 
redis-server 
Start MongoDB: If you have MongoDB installed, start it using
mongod --dbpath /path/to/your/data/db

RUN:
python red.py

python trading.py

uvicorn Api:app --host 0.0.0.0 --port 8000

Get all fraud cases:

http://localhost:8000/fraudulent-trades

Get frauds for a specific user (e.g., U1234):

http://localhost:8000/fraudulent-trades/U1234

To receive real-time fraud alerts, you can use a WebSocket client:
wscat -c ws://localhost:8000/ws


###
1. red.py
Simulates stock trade transactions.
Randomly generates trade details (user ID, stock symbol, trade type, quantity, price, etc.).
Publishes trades to a Redis stream (trade_stream).
2. trading.py
Listens to trade_stream for incoming trade data.
Detects fraudulent activities using rules like:
High-frequency trading (5+ trades in 5 seconds).
Unusual trade size (10× the average quantity).
Spoofing (quick buy-sell actions).
Geographic anomalies (trades from different locations).
Stores fraudulent trades in MongoDB.
Publishes fraud alerts to Redis (fraud_alerts channel).
3. Api.py
Provides REST API endpoints:
GET /fraudulent-trades → Fetch all fraud cases.
GET /fraudulent-trades/{user_id} → Get frauds by user.
DELETE /fraudulent-trades/{trade_id} → Mark fraud as reviewed.
WebSocket support:
Clients can subscribe to real-time fraud alerts.

