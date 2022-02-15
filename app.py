import os
import json
from cs50 import SQL
from sqlite3 import connect
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from support_functions import apology, login_required, get_current_user, sp_recipe_look_up, usd, recipe_price, single_recipe
from flask_sqlalchemy import SQLAlchemy

app =  Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filters
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["recipe_price"] = recipe_price


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# app.config["SQLALCHEMY_DATABASE_URI"] = "recipe_app.db"
# db = SQLAlchemy(app)
db = SQL("sqlite:///recipe_app.db")

# Make sure API key and API id is set
# if os.environ.get("API_KEY") == None:
#     raise RuntimeError("API_KEY not set")
# if not os.environ.get("API_ID"):
#     raise RuntimeError("API_ID not set")





@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # General Search functionaility 
    if request.method == "GET":
        return render_template("index.html")
    else:
        recipe_search = request.form.get("recipe_search")
        if not recipe_search:
            return apology("Error: Blank search request. Please input a search request")
        results = sp_recipe_look_up(recipe_search)
        if not results:
            return apology("Could not retrieve results")
        # Calculate recipe price and convert it from cents to dollars 
        # total_price = (results["pricePerServing"] * results["servings"]) / 100
        return render_template("search_results.html", results=results)
    return apology("Page Not available!")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("Please go back and enter a valid username")
        rows = db.execute("SELECT username FROM users")
        for row in rows:
            if row["username"] == username:
                return apology("Username already exists please go back and select another")
        if not password or not confirmation:
            return apology("Please Enter password and Confirm Password!")
        elif password != confirmation:
            return apology("Passwords do not match!")
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", username, generate_password_hash(password))
        row = db.execute("SELECT id FROM users WHERE username= ?", username)
        new_user_id = row[0]["id"]
        session["user_id"] = new_user_id
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/view_recipe", methods=["GET", "POST"])
def view_recipe():
    if request.method == "POST":
        recipe_id = request.form.get("recipe_id")
        image_url = request.form.get("image_url")
        recipe = single_recipe(recipe_id)
        total_price = recipe_price(recipe)
        return render_template("view_recipe.html", recipe=recipe, image_url=image_url, total_price=total_price)
    return render_template("view_recipe.html")

@app.route("/search_results")
def search_results():
    if request.method == "GET":
        return render_template("search_results.html")

@app.route("/suggestions")
def suggestions():
    if request.method == "GET":
        return render_template("suggestions.html")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    user_id = session["user_id"]
    user_prefs_IDs = db.execute("SELECT cuisine_id FROM user_preferences WHERE user_id=? AND enabled=?", user_id, 1 )
    # Grab all cusine types from DB and pass them to the settings route
    all_cuisine_types = []
    current_user_prefs = []
    cuisine_tags = db.execute("SELECT * FROM cuisine_tags")
    for cuisine in cuisine_tags:
            all_cuisine_types.append(cuisine["cuisine_type"])
            for id in user_prefs_IDs:
                if id["cuisine_id"] == cuisine["id"]:
                    current_user_prefs.append(cuisine["cuisine_type"])
    if request.method == "GET":
        user_info = db.execute("SELECT points, daily_budget FROM users WHERE id=?", user_id)
        daily_budget = user_info[0]["daily_budget"]
        if not daily_budget:
            daily_budget = 0
        daily_budget = float(daily_budget)
        return render_template("settings.html", all_cuisine_types=all_cuisine_types, current_user_prefs=current_user_prefs, daily_budget=daily_budget)
    else:
        new_budget = request.form.get("new_budget")
        cuisine_selections = request.form.getlist("cuisine_selections")
        if new_budget is not None:
            new_budget = float(new_budget)
            if new_budget > 0:
                db.execute("UPDATE users SET daily_budget=? WHERE id=?", new_budget, user_id)
        if cuisine_selections is not None:
            # create list of the ids of the users new cuisine preferences
            new_preferences_ids = []
            for cuisine in cuisine_selections:
                current_cuisine_id = db.execute("SELECT id FROM cuisine_tags WHERE cuisine_type=?", cuisine)[0]["id"]
                new_preferences_ids.append(current_cuisine_id)
            #Confirm that the selected options reflect option in DB
            for cuisine in cuisine_selections:
                if cuisine in all_cuisine_types:
                    # Check if any preferences exist for the user.If not create new ones
                    current_cuisine_id = db.execute("SELECT id FROM cuisine_tags WHERE cuisine_type=?", cuisine)[0]["id"]
                    row = db.execute("SELECT * FROM user_preferences WHERE id=? AND cuisine_id=?", user_id, current_cuisine_id)
                    print(row)
                    if not row:
                        db.execute("INSERT INTO user_preferences (user_id, cuisine_id, enabled) VALUES(?, ?, ?)", user_id, current_cuisine_id, 1 )
                        continue
                    else:
                        if row[0]["cuisine_id"] not in new_preferences_ids:
                            db.execute("UPDATE user_preferences SET enabled=0 WHERE user_id=? AND cuisine_id=?", user_id, row[0]["cuisine_id"])
                        else:
                            db.execute("UPDATE user_preferences SET enabled=1 WHERE user_id=? AND cuisine_id=?", user_id, row[0]["cuisine_id"])
        return redirect("/")
        

@app.route("/get_user_info_api")
def get_user_info_api():
    user_id = session["user_id"]
    user = get_current_user(user_id)
    username = user["username"]
    return {"value": username}




