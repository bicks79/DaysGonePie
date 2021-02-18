import os
from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")  # index.html route decorator
def index():
    return render_template("index.html")


@app.route("/recipes")  # recipes.html route decorator
def recipes():
    return render_template("recipes.html")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
