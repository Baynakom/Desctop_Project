from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta

# Initialize Firebase Admin SDK with service key
cred = credentials.Certificate("baynakom.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://baynakom-d1d3f-default-rtdb.firebaseio.com/'
})


app = Flask(__name__)


@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    if not data or "id" not in data or "username" not in data:
        return jsonify({"error": "Invalid input"}), 400
    
    ref = db.reference("devices")
    hashed_id = data["id"]
    username = data["username"]

    # Query for the ID
    username_query = ref.order_by_child("username").equal_to(username).get()
    id_query = ref.order_by_child("id").equal_to(hashed_id).get()
    if username_query: # Username exists
        key = list(username_query.keys())[0]  # Get the first matching key
        data = username_query[key]

        if hashed_id != data["id"]:
            return jsonify({"error": "Invalid input"}), 400

        expiration_date = datetime.strptime(
            data["expiration_date"], "%Y-%m-%d %H:%M:%S"
        )
        if expiration_date > datetime.now():
            return jsonify({"status": "success"}), 200  # ID is valid and not expired
        else:
            return jsonify({"error": "Invalid input"}), 400  # ID is expired
    elif not id_query: # username and id do not exist (register a new device)
        ref.push({"username": username, "id": hashed_id, "expiration_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")})
        return jsonify({"status": "success"}), 200  # ID not found
    else: # device is registered with different username
        return jsonify({"error": "Invalid input"}), 400
    
if __name__ == "__main__":
    app.run()