from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from support_functions import *
import random

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filters
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["recipe_price"] = recipe_price
app.jinja_env.filters["remove_html_tags"] = remove_html_tags


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
        user_id = session["user_id"]
        suggestion_results = get_suggestions(user_id)
        recommendations = random.sample(suggestion_results, 2)
        return render_template("index.html", recommendations=recommendations)
    else:
        recipe_search = request.form.get("recipe_search")
        if not recipe_search:
            return apology("Error: Blank search request. Please input a search request")
        recipes = sp_recipe_look_up(recipe_search)
        if not recipes:
            return apology("Could not retrieve results")
        # Calculate recipe price and convert it from cents to dollars 
        # total_price = (results["pricePerServing"] * results["servings"]) / 100
        return render_template("search_results.html", recipes=recipes)
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
    all_cuisines = []
    user_prefs = []
    cuisine_tags = db.execute("SELECT * FROM cuisine_tags")
    for cuisine in cuisine_tags:
        all_cuisines.append(cuisine)

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
        # Adding preferences selection
        daily_budget = request.form.get("daily_budget")
        cuisine_selections = request.form.getlist("cuisine_selections")
        db.execute("UPDATE users SET daily_budget=? WHERE id=?", daily_budget, new_user_id)
        for cuisine in all_cuisines:
            for selection in cuisine_selections:
                if selection == cuisine["cuisine_type"]:
                    user_prefs.append(cuisine["id"])
        for id in user_prefs:
            db.execute("INSERT INTO user_preferences (user_id, cuisine_id, enabled) VALUES (?, ?, ?)", new_user_id, id, 1)
        return redirect("/")
    else:
        return render_template("register.html", all_cuisines=all_cuisines)

@app.route("/view_recipe", methods=["GET", "POST"])
def view_recipe():
    if request.method == "POST":
        recipe_id = request.form.get("recipe_id")
        image_url = request.form.get("image_url")
        recipe = single_recipe(recipe_id)
        instructions = []
        steps = recipe["analyzedInstructions"][0]["steps"]
        for step in steps:
            instructions.append(step["step"])
        total_price = recipe_price(recipe)
        return render_template("view_recipe.html", recipe=recipe, image_url=image_url, total_price=total_price, instructions=instructions)
    return render_template("view_recipe.html")

@app.route("/search_results")
def search_results():
    if request.method == "GET":
        return render_template("search_results.html")

@app.route("/suggestions", methods=["GET", "POST"])
def suggestions():
    if request.method == "GET":
        user_id = session["user_id"]
        suggestion_results = get_suggestions(user_id)
        return render_template("suggestions.html", suggestion_results=suggestion_results)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    user_id = session["user_id"]
    user_prefs_IDs = db.execute("SELECT cuisine_id FROM user_preferences WHERE user_id=? AND enabled=?", user_id, 1 )
    # Grab all cusine types from DB and pass them to the settings route
    all_cuisine_types = []
    current_user_prefs = []
    cuisine_tags = db.execute("SELECT * FROM cuisine_tags")
    for cuisine in cuisine_tags:
            all_cuisine_types.append(cuisine)
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
            result = check_float(new_budget)
            if result == True:
                new_budget = float(new_budget)
                if new_budget > 0:
                    db.execute("UPDATE users SET daily_budget=? WHERE id=?", new_budget, user_id)
        if cuisine_selections is not None:
            # create list of the ids of the users new cuisine preferences
            new_preferences_ids = []
            for cuisine in cuisine_selections:
                print(db.execute("SELECT id FROM cuisine_tags WHERE cuisine_type=?", cuisine))
                current_cuisine_id = db.execute("SELECT id FROM cuisine_tags WHERE cuisine_type=?", cuisine)[0]["id"]
                new_preferences_ids.append(current_cuisine_id)
            #Confirm that the selected options reflect option in DB
            for cuisine in all_cuisine_types:
                if cuisine["cuisine_type"] not in cuisine_selections:
                    db.execute("UPDATE user_preferences SET enabled=0 WHERE user_id=? AND cuisine_id=?", user_id, cuisine["id"])
                else:
                    # Check if any preferences exist for the user.If not create new ones
                    row = db.execute("SELECT * FROM user_preferences WHERE user_id=? AND cuisine_id=?", user_id, cuisine["id"])
                    print(row)
                    if not row:
                        db.execute("INSERT INTO user_preferences (user_id, cuisine_id, enabled) VALUES(?, ?, ?)", user_id, cuisine["id"], 1 )
                    else:
                        db.execute("UPDATE user_preferences SET enabled=1 WHERE user_id=? AND cuisine_id=?", user_id, cuisine["id"])
                
        return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    user_id = session["user_id"]
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")
        rows = db.execute("SELECT * FROM users WHERE id=?", user_id)
        if not old_password or not new_password or not confirmation:
            return apology("Please go back and fill in password information", 403)
        if not check_password_hash(rows[0]["password_hash"], old_password):
            return apology(" Invalid password", 403)
        if new_password != confirmation:
            return apology("New password and confirmation do not match", 403)
        db.execute("UPDATE users SET password_hash=? WHERE id=?", generate_password_hash(new_password), user_id)
        return redirect("/")
    else:
        return render_template("change_password.html")


@app.route("/get_user_info_api")
def get_user_info_api():
    user_id = session["user_id"]
    if not user_id:
        return
    else:
        user = get_current_user(user_id)
        username = user["username"]
        return {"value": username}
    




