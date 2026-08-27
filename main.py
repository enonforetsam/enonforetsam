"""Single-screen terminal gif for the profile README.

One tty, nothing ever clears: the login lines type in, the MASTER OF NONE
block banner loads line by line, the prompt types a sign-off, and the gif
plays ONCE and holds on that final frame (no loop).
"""

import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

import gifos

USER = "enonforetsam"

# figlet "banner3" font, ASCII-only (the bitmap font is latin-1, no unicode block glyphs)
BANNER = [
    r"##     ##    ###     ######  ######## ######## ########      #######  ########",
    r"###   ###   ## ##   ##    ##    ##    ##       ##     ##    ##     ## ##",
    r"#### ####  ##   ##  ##          ##    ##       ##     ##    ##     ## ##",
    r"## ### ## ##     ##  ######     ##    ######   ########     ##     ## ######",
    r"##     ## #########       ##    ##    ##       ##   ##      ##     ## ##",
    r"##     ## ##     ## ##    ##    ##    ##       ##    ##     ##     ## ##",
    r"##     ## ##     ##  ######     ##    ######## ##     ##     #######  ##",
    r"",
    r"##    ##  #######  ##    ## ########",
    r"###   ## ##     ## ###   ## ##",
    r"####  ## ##     ## ####  ## ##",
    r"## ## ## ##     ## ## ## ## ######",
    r"##  #### ##     ## ##  #### ##",
    r"##   ### ##     ## ##   ### ##",
    r"##    ##  #######  ##    ## ########",
]


def main():
    t = gifos.Terminal(750, 500, 15, 15, font_size=15)
    now = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
    time_now = now.strftime("%a %b %d %I:%M:%S %p %Z %Y")

    # header + login
    t.toggle_show_cursor(False)
    t.gen_text("\x1b[93mTHE MASTER LAB v1.0 (tty1)\x1b[0m", 1, count=6)
    t.gen_text("login: ", 3, count=4)
    t.toggle_show_cursor(True)
    t.gen_typing_text(USER, 3, contin=True)
    t.gen_text("", 3, count=4, contin=True)
    t.toggle_show_cursor(False)
    t.gen_text("password: ", 4, count=4)
    t.toggle_show_cursor(True)
    t.gen_typing_text("*********", 4, contin=True)
    t.gen_text("", 4, count=4, contin=True)
    t.toggle_show_cursor(False)
    t.gen_text(f"Last login: {time_now} on tty1", 6, count=6)

    # banner loads one row per frame
    banner_top = 8
    for i, line in enumerate(BANNER):
        t.gen_text(f"\x1b[95m{line}\x1b[0m", banner_top + i, count=1)
    t.gen_text("", banner_top + len(BANNER) - 1, count=8, contin=True)

    # prompt + sign-off, then hold
    prompt_row = banner_top + len(BANNER) + 1
    t.gen_prompt(prompt_row, count=4)
    t.toggle_show_cursor(True)
    t.gen_typing_text(
        "\x1b[92m# jack of all trades, master of none. built in Kuala Lumpur.",
        prompt_row,
        contin=True,
    )
    t.toggle_blink_cursor(False)
    t.gen_text("", prompt_row, count=12, contin=True)

    # gen_gif() ignores loop_count and always loops forever; re-encode from the
    # same frames with -loop -1 so the gif plays once and holds the last frame.
    t.gen_gif()
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-r", "15", "-i", "frames/frame_%d.png",
            "-filter_complex", "[0:v] split [a][b];[a] palettegen [p];[b][p] paletteuse",
            "-loop", "-1",
            "output.gif",
        ],
        check=True,
    )
    print("INFO: output.gif re-encoded with -loop -1 (play once, hold last frame)")


if __name__ == "__main__":
    main()
