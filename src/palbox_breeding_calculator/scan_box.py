from pathlib import Path

import mss
import mss.tools


def main():
    # Project root
    project_root = Path(__file__).resolve().parent.parent.parent

    # Screenshot directory
    screenshot_dir = project_root / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    with mss.MSS() as sct:
        monitor_number = 2
        mon = sct.monitors[monitor_number]

        monitor = {
            "top": mon["top"] + 261,
            "left": mon["left"] + 882,
            "width": 636,
            "height": 530,
            "mon": monitor_number,
        }

        name = input("what's the image called? ")
        filename = name + ".png"

        output = screenshot_dir / filename

        sct_img = sct.grab(monitor)

        mss.tools.to_png(
            sct_img.rgb,
            sct_img.size,
            output=str(output),
        )

        print(output)


if __name__ == "__main__":
    main()
