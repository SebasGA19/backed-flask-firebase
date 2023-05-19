import base64
import hashlib
import io
import json
import flask
import jwt
import database


#import models

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("fir-flutterflask-firebase-adminsdk-7pnyx-c7f5f5e3f7.json")
firebase_admin.initialize_app(cred)
from firebase_admin import messaging
app = flask.Flask(__name__)

@app.route("/register", methods=["PUT"])
def register():
    req = flask.request.get_json()
    email = req["email"]
    name = req["name"]
    password = hashlib.sha512(req["password"].encode()).hexdigest()
    token =  req["token"]
    phone = req["phone"]
    position = req["position"]

    image_bytes = base64.b64decode(req["photo"])
    database.cursor.execute(
        'INSERT INTO users (email, name, password, photo, phone, position) VALUES (?, ?, ?, ?, ?, ?)', (email, name, password, image_bytes, phone, position))
    database.connection.commit()
    
    database.cursor.execute(
        'SELECT id FROM users WHERE email = ?', (email,))
    id = database.cursor.fetchall()[0][0]

    database.cursor.execute(
        'INSERT INTO TOKENS (token, user_id) VALUES (?, ?)', (token, id) )
    database.connection.commit()

    return "Register succesfull", 200

@app.route("/login", methods=["POST"])
def login():
    req = flask.request.get_json()
    email = req["email"]
    password = hashlib.sha512(req["password"].encode()).hexdigest()
    database.cursor.execute(
        'SELECT id, email, password FROM users WHERE email = ? AND password = ?', (email, password))
    user = database.cursor.fetchall()


    if user is not None and len(user) > 0:
        return flask.jsonify({"jwt": jwt.new_jwt(user[0][0], user[0][1])})
    return "Unauthorized", 401

@app.route("/message", methods=["POST"])
def message():
    req = flask.request.get_json()
    
    title = req["title"]
    body = req["body"]
    sender = req["sender"]
    email = req["email"]
    
    
    database.cursor.execute(
        'SELECT id, email, password FROM users WHERE email = ?', (email,))
    user = database.cursor.fetchall()[0][0]
    
    database.cursor.execute(
        'SELECT token FROM tokens WHERE user_id = ?', (user,))
    token = database.cursor.fetchall()[0][0]

    registration_token = token

    message = messaging.Message(
    notification=messaging.Notification(
        title=title,
        body=body
    ),
    token=registration_token,
    )
    
    response : messaging.Message 
    response = None
    
    #def __init__(self, data=None, notification=None, android=None, webpush=None, apns=None,
    #             fcm_options=None, token=None, topic=None, condition=None):

    try:
        response = messaging.send(message)
        #response.fcm_options : messaging.FCMOptions
        #dicto = {
        #"token": response.token,
        #"data": response.data,
        #"fcm_options": response.fcm_options,
        #"notification": response.notification
        #}
        print(response)
        database.cursor.execute(
        'INSERT INTO messages (title, body, sender, email, response, token) VALUES (?, ?, ?, ?, ?, ?)', (title, body, sender, email, response, registration_token) )
        database.connection.commit()
        return "Message sent", 200
    except Exception as e:
        print(e.http_response.json(), type(e))
        return "Pailas 😢👀🤢", 500
    

@app.route("/users/list", methods=["GET"])
def getUsers():
    jwt = auth(flask.request)
    email = jwt["username"]

    database.cursor.execute(
        'SELECT email, name, position  FROM users WHERE email <> ?;', (email,))
    users = database.cursor.fetchall()

    
    user_dicts = []
    for user in users:
        user_dict = {
            'email': user[0],
            'name': user[1],
            'position': user[2]
        }
        user_dicts.append(user_dict)

    return flask.jsonify(user_dicts)

@app.route("/account", methods=["GET"])
def getEmail():
    jwt = auth(flask.request)
    email = jwt["username"]

    database.cursor.execute(
        'SELECT email, name  FROM users WHERE email = ?;', (email,))
    data = database.cursor.fetchall()
    print(data)
    account_data = {
        'email': data[0][0],
        'name': data[0][1]
    }
    

    return flask.jsonify(account_data)


@app.route("/images/<email>", methods=["GET"])
def getImagen(email):
    
    database.cursor.execute(
        'SELECT photo  FROM users WHERE email = ?;', (email,))
    photo = database.cursor.fetchall()[0][0]
    
    #return flask.send_file(io.BytesIO(photo), mimetype='image/jpeg')
    return photo

def auth(request: flask.Request) -> tuple[str, int] or None:
    if "Session" not in request.headers:
        return "Unauthorized", 401
    jwt_payload = jwt.authorize(request.headers["Session"])
    if jwt_payload is None:
        return "Unauthorized", 401
    return jwt_payload
@app.route("/valid", methods=["GET"])
def valid():
    if (unauth := auth(flask.request)) is not None:
        return unauth
    return flask.jsonify({"status": "valid"})

@app.route("/send/message", methods=["POST"])
def sendMessage():
    req = flask.request.get_json()

