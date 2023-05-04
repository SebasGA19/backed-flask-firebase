import hashlib
import flask
import jwt
import database
#import models

app = flask.Flask(__name__)

@app.route("/register", methods=["PUT"])
def register():
    req = flask.request.get_json()
    email = req["email"]
    name = req["name"]
    password = hashlib.sha512(req["password"].encode()).hexdigest()
    token =  req["token"]
    photo = req["photo"]
    phone = req["phone"]
    position = req["position"]
    database.cursor.execute(
        'INSERT INTO users (email, name, password, token, photo, phone, position) VALUES (?, ?, ?, ?, ?, ?, ?)', (email, name, hashlib.sha512(password).hexdigest(), token, photo, phone, position))
    
    return "Register succesfull", 200

def auth(request: flask.Request) -> tuple[str, int] or None:
    if "Session" not in request.headers:
        return "Unauthorized", 401
    jwt_payload = jwt.authorize(request.headers["Session"])
    if jwt_payload is None:
        return "Unauthorized", 401