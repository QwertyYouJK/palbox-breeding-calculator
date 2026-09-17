import json
from collections import deque
from pathlib import Path


def pairs_dict(path):
    with open(path, "r") as file:
        pairs = json.load(file)

    # turn JSON into a dictionary
    pairs_dict = {}
    for pair in pairs:
        key = tuple(sorted([pair[0], pair[1]]))
        pairs_dict[key] = pair[2]

    return pairs_dict


def create_chain(palbox, target, pairs_dict) -> list[tuple[str, str, str]] | None:
    if target in palbox:
        print(f"Target {target} is already in the palbox.")
        return None

    parents = set(palbox)

    # Check reachability before searching all possible breeding sequences.
    reachable = parents.copy()
    while target not in reachable:
        children = set()
        for (pal, partner), child in pairs_dict.items():
            if pal != partner and pal in reachable and partner in reachable:
                children.add(child)
        if children.issubset(reachable):
            print("Target not found in the breeding tree.")
            return None
        reachable.update(children)

    seen = {frozenset(parents)}
    came_from = {}

    q = deque([(parents, 0)])

    while q:
        p, d = q.popleft()

        p_list = sorted(p)
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
                        chain = [(pal, partner, child)]
                        state = frozenset(p)
                        while state in came_from:
                            previous_state, step = came_from[state]
                            chain.append(step)
                            state = previous_state
                        chain.reverse()
                        return chain

        for (pal, partner), child in lookup.items():
            if child in p:
                continue
            new_p = p.copy()
            new_p.add(child)

            state = frozenset(new_p)
            if state in seen:
                continue
            seen.add(state)
            # Remember the exact operation that first reached this collection.
            came_from[state] = (frozenset(p), (pal, partner, child))

            q.append((new_p, d + 1))

    print("Target not found in the breeding tree.")
    return None


if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    source_dir = script_path.parent.parent.parent

    # palbox = ["54.0", "114.0", "151.0", "103.1"]
    # palbox = ["54.0", "114.0", "151.0", "103.0"]
    # palbox = ["54.0", "114.0", "151.0", "103.0", "161.0", "41.0", "191.0"]
    palbox = ["108.0", "109.0"]
    target = "91.0"
    combos = pairs_dict(source_dir / "assets" / "pairs.json")

    result = create_chain(palbox, target, combos)
    print(result)
