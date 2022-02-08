import os
import requests
import json
import re
from flask import render_template, session, redirect
from functools import wraps



def recipes_lookup(search_string):
    # Get request to EDAMAM API for recipe lookup
    try:
        search_string.replace(" ", "%")
        file = open("api_creds.json")
        json_file = json.load(file)
        api_id= json_file["APP_ID"]
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
