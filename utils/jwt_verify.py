import jwt
from datetime import datetime, timedelta, timezone
from config.config import Config

SECRET_KEY = Config.SECRET_KEY

def generate_token(data, expires_in=3600):
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        "iat": datetime.now(timezone.utc),
        "data": data
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["data"]
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    
with open("token.txt", "w") as f:
    token = generate_token({"role": "FE"}, 36000)
    f.write(token)
