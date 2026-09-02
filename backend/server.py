import os
import csv
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return jsonify({
        "message": "Zero Downtime Development Pipeline API is running"
    })


@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy"
    })


@app.route("/version")
def version():
    return jsonify({
        "version": os.getenv("APP_VERSION", "v1"),
        "environment": os.getenv("ENVIRONMENT", "local")
    })


@app.route("/deployments")
def deployments():
    records = []

    try:
        with open("/data/deployments.csv", newline="") as f:
            reader = csv.DictReader(f)
            records = list(reader)
    except FileNotFoundError:
        pass

    return jsonify({
        "total_deployments": len(records),
        "deployments": records
    })


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    conn = sqlite3.connect("/data/users.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(user["password"], password):
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    return jsonify({
        "message": "Login successful",
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)