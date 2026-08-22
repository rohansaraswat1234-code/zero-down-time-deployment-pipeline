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


if __name__ == "__main__":
    app.run(debug=True)