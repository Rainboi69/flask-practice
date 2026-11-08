"""API Gateway for Recipe Box microservices."""

import os

import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

app = Flask(__name__)

USERS_URL = "http://127.0.0.1:5001"
RECIPES_URL = "http://127.0.0.1:5002"
TIMEOUT = 1.0


def forward_request(service_url, path, internal=False):
    """Forward a request to the appropriate service."""
    url = f"{service_url}/{path}"

    headers = {}

    if request.headers.get("Authorization"):
        headers["Authorization"] = request.headers["Authorization"]

    if request.is_json:
        headers["Content-Type"] = "application/json"

    if internal:
        token = os.getenv("INTERNAL_SERVICE_TOKEN")
        if not token:
            return jsonify({"error": "gateway not configured"}), 503
        headers["X-Internal-Token"] = token

    try:
        response = requests.request(
            method=request.method,
            url=url,
            params=request.args,
            data=request.get_data(),
            headers=headers,
            timeout=TIMEOUT,
        )

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get(
                "Content-Type", "application/json"
            ),
        )

    except requests.RequestException:
        return jsonify({"error": "service unavailable"}), 503


@app.route("/register", methods=["POST"])
@app.route("/login", methods=["POST"])
@app.route("/auth/me", methods=["GET"])
def users_routes():
    return forward_request(
        USERS_URL,
        request.path.lstrip("/"),
    )


@app.route("/recipes", methods=["GET", "POST"])
@app.route("/recipes/<int:recipe_id>",
           methods=["GET", "PATCH", "DELETE"])
def recipes_routes(recipe_id=None):
    return forward_request(
        RECIPES_URL,
        request.path.lstrip("/"),
        internal=True,
    )


@app.route("/")
def home():
    return jsonify({
        "message": "Recipe Box API Gateway",
        "users_service": USERS_URL,
        "recipes_service": RECIPES_URL,
    })


@app.route("/overview", methods=["GET"])
def overview():
    result = {
        "users": None,
        "recipes": None,
        "missing": [],
    }

    checks = [
        ("users", f"{USERS_URL}/auth/me", False),
        ("recipes", f"{RECIPES_URL}/recipes", True),
    ]

    for name, url, internal in checks:
        headers = {}

        if internal:
            headers["X-Internal-Token"] = os.getenv(
                "INTERNAL_SERVICE_TOKEN", ""
            )

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=TIMEOUT,
            )

            if name == "users" and response.status_code == 401:
                result["users"] = {
                    "service": "available",
                    "authentication": "required",
                }
            elif response.ok:
                result[name] = response.json()
            else:
                result["missing"].append(name)

        except (requests.RequestException, ValueError):
            result["missing"].append(name)

    result["status"] = (
        "complete" if not result["missing"] else "partial"
    )

    return jsonify(result), 200


USERS_TIMEOUT = 1.0
RECIPES_TIMEOUT = 1.0


def fetch_service(url, headers, timeout):
    """Call one service. Returns (data, error). Never raises."""
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException:
        return None, "unavailable"

    if response.status_code == 401:
        return None, "unauthorized"
    if not response.ok:
        return None, "unavailable"

    try:
        return response.json(), None
    except ValueError:
        return None, "unavailable"


@app.route("/me", methods=["GET"])
def me():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "missing or invalid token"}), 401

    internal_token = os.getenv("INTERNAL_SERVICE_TOKEN")
    if not internal_token:
        return jsonify({"error": "gateway not configured"}), 503

    user_headers = {"Authorization": auth_header}
    recipe_headers = {
        "Authorization": auth_header,
        "X-Internal-Token": internal_token,
    }

    with ThreadPoolExecutor(max_workers=2) as pool:
        user_future = pool.submit(
            fetch_service, f"{USERS_URL}/me", user_headers, USERS_TIMEOUT
        )
        recipes_future = pool.submit(
            fetch_service, f"{RECIPES_URL}/recipes",
            recipe_headers, RECIPES_TIMEOUT,
        )
        user, user_error = user_future.result()
        recipes, recipes_error = recipes_future.result()

    if user_error == "unauthorized":
        return jsonify({"error": "invalid token"}), 401
    if user_error:
        return jsonify({"error": "users service unavailable"}), 503

    errors = {}
    if recipes_error:
        errors["recipes"] = "unavailable"
        recipes = None
    else:
        recipes = [r for r in recipes if r["owner_id"] == user["id"]]

    return jsonify({
        "user": user,
        "recipes": recipes,
        "partial": bool(errors),
        "errors": errors,
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)