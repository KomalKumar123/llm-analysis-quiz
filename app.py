import os
import time
from flask import Flask, request, jsonify

# Import your chain solver
from solver.chain_solver import solve_quiz_chain

# Create Flask app
app = Flask(__name__)

# Secret will be set as environment variable in deployment
QUIZ_SECRET = os.getenv("QUIZ_SECRET")


@app.route("/solve_quiz", methods=["POST"])
def solve_quiz():
    """
    Main webhook endpoint.
    Expects JSON: { "email": ..., "secret": ..., "url": ... }
    """
    # 1) JSON validation
    if not request.is_json:
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.get_json(silent=True) or {}
    email = data.get("email")
    secret = data.get("secret")
    url = data.get("url")

    # 2) Field validation
    if not email or not secret or not url:
        return jsonify({"error": "Missing fields"}), 400

    # 3) Secret validation
    if QUIZ_SECRET is None:
        # Developer misconfigured server
        return jsonify({"error": "Server misconfigured: QUIZ_SECRET not set"}), 500

    if secret != QUIZ_SECRET:
        return jsonify({"error": "Invalid secret"}), 403

    # 4) If secret is valid, start solving the quiz chain
    start_time = time.time()
    try:
        result = solve_quiz_chain(start_url=url, email=email, secret=secret, max_time=150)
    except Exception as e:
        # Catch any unexpected errors so your API doesn't crash
        elapsed = time.time() - start_time
        return jsonify({
            "error": "Exception while solving quiz",
            "details": str(e),
            "elapsed_seconds": elapsed
        }), 500

    elapsed = time.time() - start_time
    # Always return 200 for valid secret, even if solving failed logically,
    # because 4xx/5xx are for protocol / server errors
    return jsonify({
        "status": "completed",
        "elapsed_seconds": elapsed,
        "result": result
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """
    Simple health check endpoint.
    """
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # Run locally on http://127.0.0.1:7860
    app.run(host="0.0.0.0", port=7860, debug=True)
