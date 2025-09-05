import json
import requests


BASE_URL = "https://pokeapi.co/api/v2/type/"


damage_maps = {
    "double_damage_from": 2,
    "half_damage_from": 0.5,
    "no_damage_from": 0,
    "double_damage_to": 2,
    "half_damage_to": 0.5,
    "no_damage_to": 0,
}


with open("types.json") as f:
    type_data = json.load(f)


def generate():

    total_types = 21  # shadow and unknown and stellar are weird things, they might add stuff in future as wlel.


    # I am going to store the data as an array with one header line
    # 0 1 2 3 4 5 ... 21
    # 1 <multipliers>
    # . . .
    # Here if I call like array[1][2] it will give me the data corresponding to attacker type as 1, and defender type as 2

    array = [[1 for _ in range(total_types + 1)] for _ in range(total_types + 1)]
    array[0] = [i for i in range(total_types + 1)] 

    for i in range(1, total_types + 1):
        print("Fetching type:", i)

        try:
            data = requests.get(BASE_URL + str(i)).json()

        except:
            # Oh yeah, idk why types/20 is Not Found but types/shadow gives a value lol. Anyway it's all 1x
            print(f"Warning: Could not fetch type {i}, defaulting to 1x multipliers")
            data = {"damage_relations": {}}

        array[i] = [i] + [1] * total_types

        for k, v in data.get("damage_relations", {}).items():
            e = [type_data[_v["name"]] for _v in v if _v["name"] in type_data]

            for val in e:
                if k.endswith("_to"):
                    array[i][val] = damage_maps[k]
                elif k.endswith("_from"):
                    array[val][i] = damage_maps[k]

    with open("multipliers.json", "w+") as f:
        json.dump(array, f)

    print("Multipliers generated successfully!")

generate()
