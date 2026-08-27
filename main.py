"""Profile README gif: a demoscene-style ANSI-art piece (see art.py) revealed
top-to-bottom like a BBS download, then held. Plays ONCE, no loop.

Output is a single static screen; nothing ever clears.
"""

import subprocess

import gifos

from art import compose

COLS, ROWS = 80, 42
# terminal px = cols*8 + 2*xpad, rows*18 + 2*ypad (gohufont 14 = 8x14 + 4 line spacing)
WIDTH, HEIGHT = COLS * 8 + 30, ROWS * 18 + 30
FPS = 15

# dracula-ish ANSI roles
COLOR = {
    "bg": "0",
    "frame": "97",   # bright white
    "tex": "37",     # grey (#BFBFBF in dracula)
    "word": "95",    # pink
    "sub": "96",     # cyan
    "tag": "93",     # yellow
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
