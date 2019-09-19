from flask import Flask, Response, request, jsonify, render_template, make_response
from flask_pymongo import pymongo
from database import DatabaseConnection
from Services.UserService import UserService

import datetime
import uuid

app = Flask(__name__)
db = DatabaseConnection()
userService = UserService()

@app.route("/addNewProperty", methods=["GET"])
def getPropertyForm():
    return render_template("addNewProperty.html")

@app.route("/addNewProperty", methods=["POST"])
def addNewProperty():
    document = {
        "name": request.form["name"],
        "propertyType": request.form["type"],
        "price": request.form["price"]
    }
    db.insert("properties", document)
    return Response("Property successfully added", status=200, content_type="text/html")

@app.route("/properties", methods=["GET"])
def getProperties():
    properties = db.findMany("properties", {})
    return render_template('properties.html', properties=properties)
    
@app.route("/", methods=["GET"])
def hello():
    return Response("<h1> Hey there </h1>", status=200, content_type="text/html")

@app.route("/greeting", methods=["POST"])
def greeting():
    name = request.form["name"]
    hourOfDay = datetime.datetime.now().time().hour
    greeting = ""
    if not name:
        return Response(status=404)
    if hourOfDay < 12:
        greeting = "Good Morning "
    elif hourOfDay > 12 and hourOfDay < 18:
        greeting = "Good Afternoon "
    else:
        greeting = "Good Evening "
    response = greeting + " " + name + "!"
    return Response(response, status=200, content_type="text/html")

@app.route("/login", methods=["GET"])
def getLoginView():
    if request.cookies.get("sid"):
        return render_template("welcome.html")
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    if userService.authenticate(username, password):
        response = make_response(render_template("welcome.html"))
        sid = str(uuid.uuid4())
        session = {
            "sid": sid,
            "username": username
        }
        db.insert("sessions", session)
        response.set_cookie("sid", sid)
        return response
    else:
        return Response("Login was invalid", status=400, content_type="text/html")

@app.route("/account", methods=["GET"])
def getMyAccount():
    user = userService.authorize(request.cookies.get('sid'))
    if user:
        firstName = userService.getFirstName(user)
    else:
        return Response("Invalid session", status=400, content_type="text/html")

    return render_template("account.html", firstName=firstName)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)