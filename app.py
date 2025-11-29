import os
import time
from flask import Flask, request, jsonify

from solver.chain_solver import solve_quiz_chain

app = Flask(__name__)

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
        return jsonify({"error": "Server misconfigured: QUIZ_SECRET not set"}), 500

    if secret != QUIZ_SECRET:
        return jsonify({"error": "Invalid secret"}), 403

    # 4) Solve quiz chain with safe error handling
    start_time = time.time()
    try:
        result = solve_quiz_chain(start_url=url, email=email, secret=secret, max_time=150)
        error = None
    except Exception as e:
        # Do NOT crash the HTTP request; just report the error in JSON
        result = None
        error = str(e)

    elapsed = time.time() - start_time

    return jsonify({
        "status": "completed",
        "elapsed_seconds": elapsed,
        "error": error,
        "result": result,
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
