"""Profile README gif: a demoscene-style ANSI-art piece (see art.py) revealed
top-to-bottom like a BBS download, then held. Plays ONCE, no loop.

Output is a single static screen; nothing ever clears.
"""

import os
import subprocess

# gifos reads its palette from env at import time (GIFOS_<SCHEME>_<GROUP>_<KEY>).
# Start from dracula and override to a near-black, restrained palette:
# black bg, two greys, white, one pink accent.
PALETTE = {
    "GIFOS_GENERAL_COLOR_SCHEME": "dracula",
    "GIFOS_DRACULA_DEFAULT_COLORS_BG": "#050507",
    "GIFOS_DRACULA_DEFAULT_COLORS_FG": "#f2f2f4",   # 39: sub text
    "GIFOS_DRACULA_NORMAL_COLORS_WHITE": "#5a5a66",  # 37: texture (dim)
    "GIFOS_DRACULA_BRIGHT_COLORS_WHITE": "#a6a6b2",  # 97: frame + tags
    "GIFOS_DRACULA_BRIGHT_COLORS_MAGENTA": "#ff79c6",  # 95: the word
}
for k, v in PALETTE.items():
    os.environ[k] = v

import gifos  # noqa: E402  (must come after the env overrides)

from art import compose  # noqa: E402

COLS, ROWS = 80, 42
# terminal px = cols*8 + 2*xpad, rows*18 + 2*ypad (gohufont 14 = 8x14 + 4 line spacing)
WIDTH, HEIGHT = COLS * 8 + 30, ROWS * 18 + 30
FPS = 15

# class -> ANSI code (see PALETTE for what each code resolves to)
COLOR = {
    "bg": "0",
    "frame": "97",
    "tex": "37",
    "word": "95",
    "sub": "39",
    "tag": "97",
}


def row_to_ansi(row):
    """Serialize one grid row into a string with inline colour codes, one code
    per run of same-class cells."""
    out, cur = [], None
    for ch, cls in row:
        if cls == "bg":
            out.append(ch)
            continue
        if cls != cur:
            out.append(f"\x1b[{COLOR[cls]}m")
            cur = cls
        out.append(ch)
    out.append("\x1b[0m")
    return "".join(out).rstrip()


def main():
    grid = compose(COLS, ROWS)
    t = gifos.Terminal(WIDTH, HEIGHT, 15, 15, font_size=15)
    t.set_fps(FPS)
    t.toggle_show_cursor(False)
    t.toggle_blink_cursor(False)

    # short black hold, then the piece loads one row per frame
    t.gen_text("", 1, count=6)
    for r, row in enumerate(grid):
        t.gen_text(row_to_ansi(row), r + 1, count=1)
    # hold on the finished piece
    t.gen_text("", ROWS, count=20, contin=True)

    # gen_gif() ignores loop_count and always loops forever; re-encode from the
    # same frames with -loop -1 so the gif plays once and holds the last frame.
    t.gen_gif()
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-r", str(FPS), "-i", "frames/frame_%d.png",
            "-filter_complex", "[0:v] split [a][b];[a] palettegen [p];[b][p] paletteuse",
            "-loop", "-1",
            "output.gif",
        ],
        check=True,
    )
    print("INFO: output.gif re-encoded with -loop -1 (play once, hold last frame)")


if __name__ == "__main__":
    main()
