import sys
import json

# file_path = sys.argv[1]

# print(f"File path provided: {file_path}")

file_path = "./new_enemy.json"

with open(file_path, "r") as json_file:
    data = json.load(json_file)

# Sort the data by the "min_loc" attribute in each item
sorted_data = sorted(data.items(), key=lambda x: x[1]['attributes']['min_loc'])

# Convert the sorted data back to a dictionary
sorted_json = {str(i): item[1] for i, item in enumerate(sorted_data)}

# Write the sorted JSON back to the file
with open(file_path, "w") as json_file:
    json.dump(sorted_json, json_file, indent=3)

print("JSON file has been sorted and rewritten.")
