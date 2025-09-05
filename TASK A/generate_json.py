# THIS IS FOR TASK A
import sys
import json

import requests
    

def main():

    try:
        filename = sys.argv[1] # ngl I could've done ArgParse but this is easier since there is only 1 arguement going to be given anyway

    except IndexError:
        filename = "output.json"

    clean_data = {}

    BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

    with open("pokemon.txt", "r") as f:
        for line in f.readlines():
            base_resp = requests.get(BASE_URL + line.strip())
            type_resp = requests.get("https://pokeapi.co/api/v2/pokemon-species/" + line.strip())

            base_data = base_resp.json()
            type_data = type_resp.json()

            id = base_data["id"]
            name = base_data["name"]
            
            types = base_data["types"]
            abilities = base_data["abilities"]
            
            cleaned_types = [t["type"]["name"] for t in types]
            cleaned_abilites = [a["ability"]["name"] for a in abilities]

            is_legendary = type_data["is_legendary"]
            is_mythical = type_data["is_mythical"]
            
            clean_data[name] = {
                "id" : id,
                "name" : name,
                "types" : cleaned_types,
                "abilities" : cleaned_abilites,
                "is_legendary" : is_legendary,
                "is_mythical" : is_mythical
            }

    with open(filename , "w+") as f:
        json.dump(clean_data, f, indent=2)


main()