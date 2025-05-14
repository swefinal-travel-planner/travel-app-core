from flask import request, jsonify
from functools import wraps
from utils.jwt_verify import verify_token

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        # Xử lý trường hợp header có dạng "Bearer <token>"
        if token.startswith("Bearer "):
            token = token[7:]
        try:
            data = verify_token(token)
            print(data)
            if "role" not in data:
                return jsonify({"status":401,"message": "Missing field in payload!", }), 401
            if data["role"] != "FE" and data["role"] != "BE":
                return jsonify({"status":401,"message": "Invalid role!"}), 401
        except ValueError as e:
            return jsonify({"status":401,"message": str(e)}), 401
        return f(*args, **kwargs)
    return decorated