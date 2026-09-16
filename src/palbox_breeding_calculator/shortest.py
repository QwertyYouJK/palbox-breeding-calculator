import json
from collections import deque
from pathlib import Path


def pair_dict():
    with open(source_dir / "assets" / "pairs.json", "r") as file:
        pairs = json.load(file)

    # turn JSON into a dictionary
    pairs_dict = {}
    for pair in pairs:
        key = tuple(sorted([pair[0], pair[1]]))
        pairs_dict[key] = pair[2]

    return pairs_dict


# Find the last pair of parents to make the target, but based on breeding tree from original pals
def find_last_parents(parents, target, pairs_dict):
    seen = {frozenset(parents)}

    q = deque([(parents, 0)])
    lookup = {}

    while q:
        p, d = q.popleft()

        p_list = list(p)
        lookup = {}
        for i in range(len(p)):
            for j in range(i + 1, len(p)):
                pal = p_list[i]
                partner = p_list[j]

                key = tuple(sorted([pal, partner]))
                if key in pairs_dict:
                    child = pairs_dict[key]
                    lookup[key] = child
                    if child == target:
                        return (pal, partner)

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

    print("Target not found in the breeding tree.")
    return None, None


def create_chain(palbox, target, pairs_dict):
    if target in palbox:
        print(f"Target {target} is already in the palbox.")
        return None

    parents = set(palbox.copy())
    chain = []
    target_q = deque([target])
    # scheduled_pals = deque()

    while len(target_q) != 0:
        target = target_q.popleft()
        p1, p2 = find_last_parents(parents, target, pairs_dict)

        if p1 not in palbox and p1 not in target_q:
            target_q.append(p1)

        if p2 not in palbox and p2 not in target_q:
            target_q.append(p2)

        if p1 not in palbox or p2 not in palbox:
            target_q.append(target)

        if p1 in palbox and p2 in palbox:
            chain.append((p1, p2, target))
            palbox.append(target)

    # chain.reverse()
    return chain


if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    source_dir = script_path.parent.parent.parent

    # palbox = ["54.0", "114.0", "151.0", "103.1"]
    # palbox = ["54.0", "114.0", "151.0", "103.0"]
    # palbox = ["54.0", "114.0", "151.0", "103.0", "161.0", "41.0", "191.0"]
    palbox = ["133.0", "106.0"]
    target = "118.1"

    result = create_chain(palbox, target, pairs_dict)
    print(result)
