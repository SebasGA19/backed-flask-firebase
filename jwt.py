import json
import base64
import secrets
import time
import hashlib
import hmac
import datetime


# SECRET = secrets.token_bytes(128)
SECRET = b"test"

header = {
    "alg": "HS256",
    "typ": "JWT"
}


header_bytes = base64.urlsafe_b64encode(
    json.dumps(header, separators=(',', ':')).encode('utf-8')
).replace(b"=", b"")


def new_jwt(id: int, username: str) -> str:
    time_ahead = datetime.datetime.fromtimestamp(
        time.time()) + datetime.timedelta(days=7)
    payload = {"id": id, "username": username,
               "expires": time_ahead.timestamp()}
    payload_bytes = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(',', ':')).encode('utf-8')).replace(b"=", b"")

    signature = base64.urlsafe_b64encode(
        hmac.new(
            SECRET,
            header_bytes + b"." + payload_bytes,
            hashlib.sha256
        ).digest()
    ).replace(b"=", b"")
    return f"{header_bytes.decode()}.{payload_bytes.decode()}.{signature.decode()}"


def authorize(jwt: str) -> dict or None:
    try:
        h, p, signature = jwt.split('.')
        computed_signature = base64.urlsafe_b64encode(
            hmac.new(
                SECRET,
                f"{h}.{p}".encode(),
                hashlib.sha256
            ).digest()
        ).replace(b"=", b"").decode()
        if computed_signature != signature:
            return None
        p += "=" * (len(p) % 4)
        payload = json.loads(base64.b64decode(p))

        if "expires" not in payload:
            return None
        if time.time() >= payload["expires"]:
            return None
        return payload
    except ValueError:
        return None
