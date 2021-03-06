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
    with open("data/recipeImage.json", "r") as json_data:
        data = json.load(json_data)
        recipes = list(mongo.db.recipes.find())
        ingredients = list(mongo.db.ingredients.find())
        method = list(mongo.db.method.find())
    return render_template(
        "recipes.html", page_title="Recipes",
        recipes=recipes,
        ingredients=ingredients,
        method=method,
        recipeImage=data)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipes.html", recipes=recipes)


@app.route("/feature")  # feature.html route decorator
def feature():
    with open("data/feature.json", "r") as json_data:
        data = json.load(json_data)
    return render_template(
        "feature.html", page_title="Feature", feature=data)


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
        return redirect(url_for("profile", username=session["user"]))
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
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password
                flash("Incorrect Username/Password.")
                return redirect(url_for('login'))
        else:
            # username does not exist
            flash("Incorrect Username/Password.")
            return redirect(url_for('login'))
    return render_template("login.html", page_title="Login")


# profile.html route decorator
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    ingredients = list(mongo.db.ingredients.find())
    method = list(mongo.db.method.find())
    categories = mongo.db.categories.find().sort("categories", 1)
    # adding a new recipe to mongodb
    if request.method == "POST":
        recipe = {
            "category_name": request.form.get("category_name"),
            "recipe_title": request.form.get("recipe_title"),
            "serves": request.form.get("serves"),
            "prep_time": request.form.get("prep_time"),
            "cook_time": request.form.get("cook_time"),
            "desc": request.form.get("desc"),
            "created_by": session["user"]
            }
        ingredients = {
            "category_name": request.form.get("category_name"),
            "recipe_title": request.form.get("recipe_title"),
            "components": request.form.get("components").split(',')
            }
        method = {
            "category_name": request.form.get("category_name"),
            "recipe_title": request.form.get("recipe_title"),
            "process": request.form.get("process").split(',')
            }

        mongo.db.recipes.insert_one(recipe)
        mongo.db.ingredients.insert_one(ingredients)
        mongo.db.method.insert_one(method)
        flash("Recipe added to your kitchen")
        return redirect(url_for('profile', username=username))

    # return username from mongodb
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    # finding recipe by session user
    recipes = list(mongo.db.recipes.find({'created_by': username}))
    if session["user"]:
        return render_template(
            "profile.html",
            username=username,
            recipes=recipes,
            ingredients=ingredients,
            method=method,
            categories=categories
            )

    return redirect(url_for('login'))


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "recipe_title": request.form.get("recipe_title"),
            "serves": request.form.get("serves"),
            "prep_time": request.form.get("prep_time"),
            "cook_time": request.form.get("cook_time"),
            "desc": request.form.get("desc"),
            "created_by": session["user"]
            }
        ingredients = {
            "category_name": request.form.get("category_name"),
            "recipe_title": request.form.get("recipe_title"),
            "components": request.form.get("components").split(',')
            }
        method = {
            "category_name": request.form.get("category_name"),
            "recipe_title": request.form.get("recipe_title"),
            "process": request.form.get("process").split(',')
            }

        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, submit)
        mongo.db.ingredients.insert_one(ingredients)
        mongo.db.method.insert_one(method)
        flash("Your recipe has been altered")

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("categories", 1)
    return redirect(url_for(
        'profile',
        recipe=recipe,
        categories=categories,
        username=session["user"]))


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    # delete user recipe
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("The recipe has been removed from your kitchen.")
    return redirect(url_for('profile', username=session["user"]))


@app.route("/logout")
def logout():
    # remove user from cookies
    flash("You have been logged out.")
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=False)
