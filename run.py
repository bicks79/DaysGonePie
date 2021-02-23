import os
import json
from flask import(
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.special_ingredient = os.environ.get("SPECIAL_INGREDIENT")


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


@app.route("/login", methods=["GET", "POST"])  # feature.html route decorator
def login():
    return render_template("login.html", page_title="Login")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)
