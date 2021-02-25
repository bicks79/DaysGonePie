import os
import json
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")  # index.html route decorator
def index():
    data = []
    with open("data/card.json", "r") as json_data:
        data = json.load(json_data)
    return render_template("index.html", card=data)


@app.route("/recipes")  # recipes.html route decorator
def recipes():
    bread_recipes = mongo.db.bread.find()
    cake_recipes = mongo.db.cakes.find()
    dessert_recipes = mongo.db.desserts.find()
    pastry_recipes = mongo.db.pastry.find()
    return render_template(
        "recipes.html", page_title="Recipes",
        bread_recipes=bread_recipes,
        cake_recipes=cake_recipes,
        dessert_recipes=dessert_recipes,
        pastry_recipes=pastry_recipes)


@app.route("/recipe_card")  # recipe_card.html route decorator
def recipe_card():
    return render_template("recipe_card.html", page_title="Recipe Card")


@app.route("/feature")  # feature.html route decorator
def feature():
    return render_template("feature.html", page_title="Feature")


@app.route(
    "/register", methods=["GET", "POST"])  # register.html route decorator
def register():
    if request.method == "POST":   # Check if username already exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username in use")
            return redirect(url_for("register"))

        register_user = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register_user)

        session["user"] = request.form.get("username").lower()
        flash("Welcome to Days Gone Pie!")
    return render_template("register.html", page_title="Register")


@app.route("/login", methods=["GET", "POST"])  # login.html route decorator
def login():
    if request.method == "POST":
        # checking for user in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # check password match
            if check_password_hash(
               existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("password").lower()
                flash("Welcome, {}".format(request.form.get("username")))
            else:
                # invalid password
                flash("Incorrect Username/Password, please try again.")
                return redirect(url_for('login'))
        else:
            # username does not exist
            flash("Incorrect Username/Password.")
            return redirect(url_for('login'))

    return render_template("login.html", page_title="Login")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)
