import os
import requests
import json
import re
from cs50 import SQL
from flask import render_template, session, redirect
from functools import wraps
from dotenv import load_dotenv


db = SQL("sqlite:///recipe_app.db")
load_dotenv()
api_key = os.getenv("APIKEY")

def usd(value):
    #Format value to usd
    return f"${value:,.2f}"

def recipe_price(recipe):
    return float(recipe["pricePerServing"]) * float(recipe["servings"]) / 100

def check_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False

def remove_html_tags(text):
    """Remove html tags from a string"""
    """ referenced from this source https://medium.com/@jorlugaqui/how-to-strip-html-tags-from-a-string-in-python-7cb81a2bbf44"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_current_user(user_id):
        user_info = {}
        row = db.execute("SELECT * FROM users WHERE id=?", user_id)
        user_info["username"] = row[0]["username"]
        user_info["points"] = row[0]["points"]
        user_info["daily_budget"] = row[0]["daily_budget"]
        user_prefs_IDs = db.execute("SELECT cuisine_id FROM user_preferences WHERE user_id=? AND enabled=?", user_id, 1 )
        current_user_prefs = []
        cuisine_tags = db.execute("SELECT * FROM cuisine_tags")
        for cuisine in cuisine_tags:
            for id in user_prefs_IDs:
                if id["cuisine_id"] == cuisine["id"]:
                    current_user_prefs.append(cuisine["cuisine_type"])
        user_info["preferences"] = current_user_prefs
        return user_info


def single_recipe(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"
    response = requests.get(url)
    recipe = json.loads(response.text)
    return recipe

def sp_recipe_look_up(search_string):
    get_ids_url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={api_key}&query={search_string}"
    get_ids_response = requests.get(get_ids_url)
    json_data = json.loads(get_ids_response.text)
    ids = []
    for item in json_data["results"]:
        ids.append(str(item["id"]))
    if not ids:
        return None
    ids_string = ','.join(ids)
    print(f"IDs= {ids_string}")
    get_recipes_url = f"https://api.spoonacular.com/recipes/informationBulk?apiKey={api_key}&ids={ids_string}"
    get_recipes_resp = requests.get(get_recipes_url)
    recipes = json.loads(get_recipes_resp.text)

    return recipes
    

def get_suggestions(user_id):
    cuisine_IDs = db.execute("SELECT * FROM user_preferences WHERE user_id = ?", user_id)
    user_budget = db.execute("SELECT points, daily_budget FROM users WHERE id=?", user_id)
    user_budget = float(user_budget[0]["daily_budget"])
    rows = db.execute("SELECT * FROM cuisine_tags")
    users_preferences = []
    for row in rows:
        for id in cuisine_IDs:
            if id["cuisine_id"] == row["id"] and id["enabled"] == 1:
                users_preferences.append(row["cuisine_type"])

    total_results = []
    for preference in users_preferences:
        url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={api_key}&cuisine={preference}&addRecipeInformation=True"
        response = requests.get(url)
        json_data = json.loads(response.text)
        total_results.append(json_data["results"])
    

    suggestion_results = []
    for results in total_results:
        for recipe in results:
            price = recipe_price(recipe)
            print(f"PRICE: {price}")
            print(f"user_budget: {user_budget}")
            if price <= user_budget:
                suggestion_results.append(recipe)
        

    return suggestion_results


# with open("api_test2.json", "w") as file:
#     recipe = single_recipe(641128)
#     json.dump(recipe, file)



