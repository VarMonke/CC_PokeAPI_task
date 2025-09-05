import json

from aiohttp import web
import requests

types_dict = json.load(open("types.json", "r"))
reversed_types_dict = {v: k for k, v in types_dict.items()}
multipliers = json.load(open("multipliers.json", "r"))


def return_type_from_name(name: str):
    """
    This method is primarily used for getting the types of a defender Pokemon.
    Useless for attackers since a move can be a single type only. (Rip Meta if there were dual type moves)
    """

    types = [t.strip().lower() for t in name.split(",")]

    if all(t in types_dict for t in types):
        return types

    resp = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}")

    if resp.status_code != 200:
        return ("UNKNOWN_POKEMON", name, resp.status_code)

    data = resp.json()
    types = [t["type"]["name"] for t in data["types"]]

    return types


async def root(request: web.Request):
    """
    This is the main request handling function, this sanitizes the attacker type and defender type(s) into a number (1-20),
    which is mapped in `multipliers.json`, a file that contains multipliers created by `generate_multiplier.py`.
    """

    attacker_name = request.query.get("attacker", None)
    defender_name = request.query.get("defender", None)

    if attacker_name and defender_name:
        attacker_id = types_dict.get(attacker_name)
        defender_ids = [types_dict.get(t) for t in return_type_from_name(defender_name)]
        
        multiplier = 1
    
        for def_id in defender_ids:
            multiplier *= multipliers[attacker_id][def_id]
        
        resp_json = {
            "attacker": attacker_name,
            "defender": defender_name,
            "multiplier": multiplier,
        }

        return web.json_response(resp_json)

    elif attacker_name:  
        attacker_id = types_dict.get(attacker_name)
        if attacker_id is None:
            return web.json_response({"error": f"Unknown attacker type: {attacker_name}. You cannot enter pokemon names for attackers, only enter the type of attack used."}, status=400)

        to_defenders = {
            reversed_types_dict[i]: multipliers[attacker_id][i] for i in range(1, 19)
        }

        return web.json_response({"attacker": attacker_name, "to_defenders": to_defenders})

    elif defender_name: 
        defender_types = return_type_from_name(defender_name)
        defender_ids = [types_dict.get(t) for t in defender_types]

        if defender_types[0] == "UNKNOWN_POKEMON":
            return web.json_response({"Invalid Pokemon Name" : defender_types[1]}, status=int(defender_types[2]))


        # I'm not including the other type multipliers because the requirements do not ask for it.                                      
        type_multipliers = {
            "4x_weaknesses": [],
            "2x_weaknesses": [],
            "immunities": [],
        }

        for attacker_id, attack_name in reversed_types_dict.items():

            multiplier = 1

            for def_id in defender_ids:
                multiplier *= multipliers[attacker_id][def_id]

            if multiplier == 4:
                type_multipliers["4x_weaknesses"].append(attack_name)

            elif multiplier == 2:
                type_multipliers["2x_weaknesses"].append(attack_name)

            elif multiplier == 0:
                type_multipliers["immunities"].append(attack_name)


        resp_json = {
            "defender": defender_name,
            "types": defender_types,
            "multiplier" : multiplier,
            **type_multipliers,
        }

        return web.json_response(resp_json)

    else:
        return web.json_response({"error": "Invalid or missing attacker/defender name"}, status=400)


app = web.Application()
app.router.add_get("/", root)

if __name__ == "__main__":
    print("RUNNING WEB SERVER ON https://127.0.0.1:8000\nIf you can't reach the web server, please try changing the port in web.run_app()'s port parameter.")
    web.run_app(app, host="127.0.0.1", port=8000)
