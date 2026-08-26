import os
import csv
from flask import Flask, jsonify

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)