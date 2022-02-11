import os
import requests
import json
import re
from cs50 import SQL
from flask import render_template, session, redirect
from functools import wraps

db = SQL("sqlite:///recipe_app.db")



def usd(value):
    #Format value to usd
    return f"${value:,.2f}"

def recipe_price(recipe):
    return float(recipe["pricePerServing"]) * float(recipe["servings"]) / 100


def recipes_lookup(search_string):
    # Get request to EDAMAM API for recipe lookup
    try:
        search_string.replace(" ", "%")
        file = open("api_creds.json")
        json_file = json.load(file)
        api_id= json_file["API_ID"]
        api_key=json_file["API_KEY"]
        file.close()
        url = f"https://api.edamam.com/api/recipes/v2?type=public&q={search_string}&app_id={api_id}&app_key={api_key}"

        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # start the process of parsing the response
    json_data = json.loads(response.text)
    recipes = []
    items = json_data["hits"]
    # Create regex statement that parses the uri of a recipe item to grab the recipes ID 
    reg = re.compile("recipe.+")

    #Create a consolidated dict of recipes 
    for item in items:
        item_info = item["recipe"]
        recipe = {}
        recipe["id"] = re.findall(reg, item_info["uri"])
        recipe["name"] = item_info["label"]
        recipe["image"] = item_info["image"] 
        recipe["source_url"] = item_info["url"]
        recipe["ingredients"] = item_info["ingredientLines"]
        recipe["calories"] = item_info["calories"]
        recipe["total_time"] = item_info["totalTime"]
        recipe["servings"] = item_info["yield"]
        recipe["cuisine/dish_type"] = (item_info["cuisineType"], item_info["dishType"])
        recipes.append(recipe)

    return recipes

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
        return user_info


def single_recipe(recipe_id):
    file = open("spoon_api_creds.json", 'r')
    json_file = json.load(file)
    api_key = json_file["apiKey"]
    file.close()
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"
    response = requests.get(url)
    recipe = json.loads(response.text)
    return recipe

def sp_recipe_look_up(search_string):
    search_string.replace(" ", "%")
    file = open("spoon_api_creds.json")
    json_file = json.load(file)
    api_key = json_file["apiKey"]
    file.close()
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
    



