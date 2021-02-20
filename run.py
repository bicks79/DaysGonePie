import os
import json
from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")  # index.html route decorator
def index():
    data = []
    with open("data/card.json", "r") as json_data:
        data = json.load(json_data)
    return render_template("index.html", card=data)


@app.route("/recipes")  # recipes.html route decorator
def recipes():
    return render_template("recipes.html", page_title="Recipes")


@app.route("/feature")  # feature.html route decorator
def feature():
    return render_template("feature.html", page_title="Feature")


@app.route("/login")  # feature.html route decorator
def login():
    return render_template("login.html", page_title="Login")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
