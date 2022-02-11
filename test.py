import requests
import json

# # response = requests.get("https://api.spoonacular.com/recipes/extract?apiKey=f0296f9d4ea7493b80fc0dbccfaa7349&url=https://www.theblackpeppercorn.com/trinidad-style-curry-chicken")

# response = requests.get("https://api.spoonacular.com/recipes/complexSearch?apiKey=f0296f9d4ea7493b80fc0dbccfaa7349&query=trinidad%curry%")

# with open("api_test.json", 'w') as file:
#     file.write(response.text)

# print(response.text)

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
    ids_string = ','.join(ids)
    print(f"IDs= {ids_string}")
    get_recipes_url = f"https://api.spoonacular.com/recipes/informationBulk?apiKey={api_key}&ids={ids_string}"
    get_recipes_resp = requests.get(get_recipes_url)
    json_data = json.loads(get_recipes_resp.text)

    with open("api_test.json", 'w') as file:
        json.dump(json_data, file)
    print(json_data)

sp_recipe_look_up("curry")



    

