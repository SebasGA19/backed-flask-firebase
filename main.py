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

@app.route("/login", methods=["POST"])
def login():
    req = flask.request.get_json()
    email = req["email"]
    password = hashlib.sha512(req["password"].encode()).hexdigest()
    token = req["token"]
    database.cursor.execute(
        'SELECT id, email, password, token FROM users WHERE email = ? AND password = ? AND token = ?', (email, password))
    user = database.cursor.fetchall()
    
    if user is not None and len(user) > 0:
        return flask.jsonify({"jwt": jwt.new_jwt(user[0][0], user[0][1])})
    return "Unauthorized", 401

def auth(request: flask.Request) -> tuple[str, int] or None:
    if "Session" not in request.headers:
        return "Unauthorized", 401
    jwt_payload = jwt.authorize(request.headers["Session"])
    if jwt_payload is None:
        return "Unauthorized", 401
    
@app.route("/valid", methods=["GET"])
def valid():
    if (unauth := auth(flask.request)) is not None:
        return unauth
    return flask.jsonify({"status": "valid"})