from flask import Flask, redirect, render_template, request, session 

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

@app.route("/login")
def login():
    if request.method == "GET":
        return render_template("login.html")

@app.route("/register")
def register():
    if request.method == "GET":
        return render_template("register.html")

@app.route("/view_recipe")
def view_recipe():
    if request.method == "GET":
        return render_template("view_recipe.html")

@app.route("/search_results")
def search_results():
    if request.method == "GET":
        return render_template("search_results.html")

@app.route("/suggestions")
def suggestions():
    if request.method == "GET":
        return render_template("suggestions.html")

@app.route("/settings")
def settings():
    if request.method == "GET":
        return render_template("settings.html")


