import os
import time
import secrets
import sqlite3
import subprocess

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash

app = Flask(__name__)
CORS(app)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "users.db")

ADMIN_TOKENS = {}
TOKEN_EXPIRY = 3600


def verify_admin(email, password):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return False

    if user["role"] != "admin":
        return False

    return check_password_hash(user["password"], password)


def create_token(email):
    token = secrets.token_urlsafe(32)

    ADMIN_TOKENS[token] = {
        "email": email,
        "expires": time.time() + TOKEN_EXPIRY
    }

    return token


def admin_authorized():
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return False

    token = auth.split(" ", 1)[1]

    token_data = ADMIN_TOKENS.get(token)

    if not token_data:
        return False

    if time.time() > token_data["expires"]:
        ADMIN_TOKENS.pop(token, None)
        return False

    return True


@app.route("/control/health")
def control_health():
    return jsonify({
        "status": "healthy",
        "service": "deployment-control"
    })


@app.route("/control/admin-login", methods=["POST"])
def admin_login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password required"
        }), 400

    if not verify_admin(email, password):
        return jsonify({
            "message": "Admin authentication failed"
        }), 401

    token = create_token(email)

    return jsonify({
        "message": "Admin authenticated",
        "token": token,
        "expires_in": TOKEN_EXPIRY
    })


@app.route("/admin/deploy", methods=["POST"])
def admin_deploy():

    if not admin_authorized():
        return jsonify({
            "message": "Unauthorized"
        }), 401

    result = subprocess.run(
        ["./deployment/scripts/deploy.sh"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=180
    )

    if result.returncode != 0:
        return jsonify({
            "message": "Deployment failed",
            "output": result.stdout,
            "error": result.stderr
        }), 500

    return jsonify({
        "message": "Deployment completed successfully",
        "output": result.stdout
    })


@app.route("/admin/rollback", methods=["POST"])
def admin_rollback():

    if not admin_authorized():
        return jsonify({
            "message": "Unauthorized"
        }), 401

    result = subprocess.run(
        ["./deployment/scripts/rollback.sh"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        return jsonify({
            "message": "Rollback failed",
            "output": result.stdout,
            "error": result.stderr
        }), 500

    return jsonify({
        "message": "Rollback completed successfully",
        "output": result.stdout
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000)
