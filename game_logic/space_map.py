import json

file_path = "data/space_map.json"
# file_path = "../data/space_map.json"  # debug path


async def read_map(gps: int) -> list:
    try:
        with open(file_path, "r") as json_file:
            map_data = json.load(json_file)
            # print(f"comparing gps={gps} and len(map_data)={len(map_data)}")
            if len(map_data) >= gps:
                loc = map_data.get(str(gps), None)
                return loc
            else:
                return None
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")


async def name(gps: int) -> str:
    loc = await read_map(gps=gps)
    loc_name = loc
    return loc_name.get("name")


async def loc_type(gps: int) -> str:
    loc = await read_map(gps=gps)
    loc_name = loc
    return loc_name.get("type")


async def features(gps: int) -> list:
    loc = await read_map(gps=gps)
    loc_name = loc
    return loc_name.get("features")


async def events(gps: int):
    loc = await read_map(gps=gps)
    loc_name = loc
    return loc_name.get("events_weights")


async def event_details(gps: int):
    loc = await read_map(gps=gps)
    loc_name = loc
    return loc_name.get("event_details")
