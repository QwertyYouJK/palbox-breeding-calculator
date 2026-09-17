import json
from pathlib import Path

import numpy as np
from PIL import Image


def load_references(icon_dir, slot_size=106):
    with open(icon_dir / "icon_map.json", "r", encoding="utf-8") as file:
        icon_map = json.load(file)

    # Compare inside the circle, excluding the usual badge/sparkle corners.
    y, x = np.ogrid[:slot_size, :slot_size]
    centre = (slot_size - 1) / 2
    distance_squared = (x - centre) ** 2 + (y - centre) ** 2
    mask = distance_squared < (slot_size * 0.425) ** 2
    corner_size = round(slot_size * 0.3)
    mask[:corner_size, :corner_size] = False
    mask[:corner_size, -corner_size:] = False

    ids = []
    colours = []
    opacity = []
    for entry in icon_map:
        for filename, pal_id in entry.items():
            with Image.open(icon_dir / filename) as image:
                original = image.convert("RGBA")
                # Keep a few sizes because the screenshot and source icons differ.
                scale = 0.83
                size = round(slot_size * scale)
                resized = original.copy()
                resized.thumbnail((size, size), Image.Resampling.LANCZOS)
                canvas = Image.new("RGBA", (slot_size, slot_size))
                left = (slot_size - resized.width) // 2
                top = (slot_size - resized.height) // 2
                canvas.paste(resized, (left, top))

                pixels = np.asarray(canvas, dtype=np.float32)[mask] / 255
                ids.append(pal_id)
                colours.append(pixels[:, :3] * pixels[:, 3:4])
                opacity.append(pixels[:, 3:4])

    if not ids:
        raise ValueError("The icon map contains no reference icons.")

    return {
        "ids": ids,
        "colours": np.stack(colours),
        "opacity": np.stack(opacity),
        "mask": mask,
        "background_mask": distance_squared > (slot_size * 0.47) ** 2,
        "slot_size": slot_size,
    }


def identify_pal(cropped, references, min_score=0.78, min_margin=0.03):
    # These are starting thresholds to tune against labelled screenshots.
    size = references["slot_size"]
    if cropped.size != (size, size):
        raise ValueError(f"Expected a {size} x {size} slot crop.")

    pixels = np.asarray(cropped.convert("RGB"), dtype=np.float32) / 255
    mask = references["mask"]
    # A nearly uniform slot has too little detail to identify reliably.
    if np.std(pixels[mask], axis=0).mean() < 0.025:
        return {"id": None, "score": 0.0, "margin": 0.0, "candidates": []}

    # Blend transparent reference pixels onto the slot's estimated background.
    background = np.median(pixels[references["background_mask"]], axis=0)
    templates = references["colours"] + (1 - references["opacity"]) * background

    best_scores = np.zeros(len(references["ids"]), dtype=np.float32)
    padded = np.pad(pixels, ((2, 2), (2, 2), (0, 0)), mode="edge")
    for dy in (-2, 0, 2):
        for dx in (-2, 0, 2):
            shifted = padded[2 + dy : 2 + dy + size, 2 + dx : 2 + dx + size]
            error = np.mean((templates - shifted[mask]) ** 2, axis=(1, 2))
            scores = 1 - np.sqrt(error)
            best_scores = np.maximum(best_scores, scores)

    # Multiple sizes or icons for the same Pal count as one candidate.
    scores_by_id = {}
    for pal_id, score in zip(references["ids"], best_scores):
        scores_by_id[pal_id] = max(scores_by_id.get(pal_id, 0.0), float(score))

    candidates = sorted(scores_by_id.items(), key=lambda item: item[1], reverse=True)
    best_id, best_score = candidates[0]
    second_score = candidates[1][1] if len(candidates) > 1 else 0.0
    margin = best_score - second_score
    accepted = best_score >= min_score and margin >= min_margin

    return {
        "id": best_id if accepted else None,
        "score": best_score,
        "margin": margin,
        "candidates": candidates[:3],
    }


def main():
    # Project root
    project_root = Path(__file__).resolve().parent.parent.parent

    # Screenshot directory
    screenshot_dir = project_root / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    filename = "page 2.png"
    image_path = screenshot_dir / filename

    # load all the pal icons
    references = load_references(project_root / "assets" / "pal_icons")

    with open(project_root / "assets" / "catalog.json", "r", encoding="utf-8") as file:
        catalog = json.load(file)
    names = {pal["id"]: pal["names"]["en"] for pal in catalog}

    with Image.open(image_path) as img:
        for i in range(30):
            # crop image 106 x 106
            left = (i % 6) * 106
            top = (i // 6) * 106
            right = left + 106
            bottom = top + 106
            cropped = img.crop((left, top, right, bottom))
            # cropped.show()

            result = identify_pal(cropped, references)

            if result["id"] is None:
                print("Unknown or uncertain Pal.")
            else:
                pal_id = result["id"]
                print(f"Identified: {names.get(pal_id, pal_id)} (ID: {pal_id})")
            # print(f"Similarity: {result['score']:.3f}; margin: {result['margin']:.3f}")
            # for pal_id, score in result["candidates"]:
            #     print(f"  {names.get(pal_id, pal_id)}: {score:.3f}")


if __name__ == "__main__":
    main()
