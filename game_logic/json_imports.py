import json


def read_players() -> list:
    file_path = "data/new_player_ship.json"
    try:
        with open(file_path, "r") as json_file:
            new_player = json.load(json_file)
            return new_player
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")


def player_abilities():
    new_player = read_players()
    return json.dumps(new_player.get("abilities"))
    

def player_ship_slots():
    new_player = read_players()
    return json.dumps(new_player.get("ship_slots"))    


def player_attributes():
    new_player = read_players()
    return json.dumps(new_player.get("attributes"))


def read_enemies() -> list:
    enemies_file_path = "data/new_enemy.json"
    try:
        with open(enemies_file_path, "r") as json_file:
            new_enemy = json.load(json_file)
            return new_enemy
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except FileNotFoundError:
        print(f"File not found: {enemies_file_path}")


def read_items() -> list:
    read_items_file_path = "data/new_items.json"
    try:
        with open(read_items_file_path, "r") as json_file:
            new_item = json.load(json_file)
            return new_item
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except FileNotFoundError:
        print(f"File not found: {read_items_file_path}")


def read_materials() -> list:
    read_items_file_path = "data/new_material.json"
    try:
        with open(read_items_file_path, "r") as json_file:
            new_item = json.load(json_file)
            return new_item
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except FileNotFoundError:
        print(f"File not found: {read_items_file_path}")
