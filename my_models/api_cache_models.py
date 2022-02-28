from abc import ABC, abstractmethod
from cs50 import SQL
import json

import requests
from urllib.parse import urlencode

class Api_Cache_Obj(ABC):

    def __init__(self, db_instance: SQL, api_credentials):
        print("Initialized")
        self.database = db_instance
        self.api_credentials = api_credentials
        self.ensure_table_existence()
    
    @property
    @abstractmethod
    def api_endpoint(self):
        pass

    @property
    @abstractmethod
    def table_name(self):
        pass

    def ensure_table_existence(self):
        self.database.execute("DROP TABLE if exists ?", self.table_name)
        self.database.execute("CREATE TABLE if not exists ? (query_url TEXT, results TEXT, PRIMARY KEY(query_url))", self.table_name)

    def query_api(self, url):
        response = requests.get(url)
        self.save_query_data(url, response.text)
        response = json.loads(response.text)
        return response

    def check_cache(self, url):
        content = self.database.execute("SELECT * from ? where query_url = ?", self.table_name, url)
        return json.loads(content) if content else None

    def save_query_data(self, url, results):
        self.database.execute("INSERT INTO ? (query_url, results) VALUES (?, ?)", self.table_name, url, results)

    def get_data(self, query_path, query_params={}):
        query_params['apiKey'] = self.api_credentials
        url = f"{self.api_endpoint}/{query_path.strip('/')}?{urlencode(query_params)}"

        content = self.check_cache(url)
        if not content:
            content = self.query_api(url)

        return content

class Spoonacular_Api_Handler(Api_Cache_Obj):
    
    api_endpoint = "https://api.spoonacular.com"
    table_name = "spoonacular_cache"

