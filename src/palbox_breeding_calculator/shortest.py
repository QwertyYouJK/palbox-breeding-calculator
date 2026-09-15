import json
import sys
from collections import deque
from pathlib import Path

script_path = Path(__file__).resolve()
source_dir = script_path.parent.parent.parent

# palbox = ["54.0", "114.0", "151.0", "103.1"]
palbox = ["54.0", "114.0", "151.0", "103.0"]
# palbox = ["160.0", "137.0"]
target = "139.0"

if target in palbox:
    print(f"Target {target} is already in the palbox.")
    sys.exit(0)

parents = set(palbox.copy())

with open(source_dir / "assets" / "pairs.json", "r") as file:
    pairs = json.load(file)

# turn JSON into a dictionary
pairs_dict = {}
for pair in pairs:
    key = tuple(sorted([pair[0], pair[1]]))
    pairs_dict[key] = pair[2]

seen = {frozenset(parents)}

q = deque([(parents, 0)])
idx = 0
while q:
    p, d = q.popleft()

    p_list = list(p)
    lookup = {}
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            pal = p_list[i]
            partner = p_list[j]

            # Check if the pair exists in the pairs data
            key = tuple(sorted([pal, partner]))
            if key in pairs_dict:
                child = pairs_dict[key]
                lookup[key] = child

    if target in lookup.values():
        print(f"Target {target} found at depth {d + 1}.")
        print(
            f"Parents of target: {[(k, v) for k, v in lookup.items() if v == target]}"
        )
        break

    for child in set(lookup.values()):
        if child in p:
            continue
        new_p = p.copy()
        new_p.add(child)

        state = frozenset(new_p)
        if state in seen:
            continue
        seen.add(state)

        q.append((new_p, d + 1))
else:
    print("Target not found in the breeding tree.")
