import json
from pathlib import Path

script_path = Path(__file__).resolve()
source_dir = script_path.parent.parent.parent

pal1 = input("Enter the name of the first pal: ")
pal2 = input("Enter the name of the second pal: ")

pal1 = pal1.strip().lower().replace(" ", "-")
pal2 = pal2.strip().lower().replace(" ", "-")

with open(source_dir / "assets" / "catalog.json", "r") as file:
    catalog = json.load(file)
  
pal1_found = False
pal2_found = False

id1 = None
id2 = None

for pal_data in catalog:
    if pal_data["slug"] == pal1:
        print(f"First pal ID: {pal_data['paldexNo']}, internal ID: {pal_data['id']}")
        pal1_found = True
        id1 = pal_data['id']
    if pal_data["slug"] == pal2:
        print(f"Second pal ID: {pal_data['paldexNo']}, internal ID: {pal_data['id']}")
        pal2_found = True
        id2 = pal_data['id']

if not pal1_found or not pal2_found:
    print(f"One of the pals is not found: {pal1} or {pal2}")
    exit(1)
        

with open(source_dir / "assets" / "pairs.json", "r") as file:
    pairs = json.load(file)

for pair in pairs:
    parent1 = pair[0]
    parent2 = pair[1]
    child = pair[2]
    if (parent1 == id1 and parent2 == id2) or (parent1 == id2 and parent2 == id1):
        for pal_data in catalog:
            if pal_data["id"] == child:
                print(f"Breeding result: id = {child}, name = {pal_data['names']['en']}")
        exit(0)

print("No valid breeding pair found.")