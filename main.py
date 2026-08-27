"""Profile README gif: a demoscene-style ANSI-art piece (see art.py). The word,
frame and text are static; the dot-texture field around them drifts downward
with parallax, as a seamless infinite loop.
"""

import os

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

from art import LOOP_FRAMES, animate_texture, compose  # noqa: E402

COLS, ROWS = 106, 30  # ~878x570px: fills GitHub's README column at 1:1, no downscale
# terminal px = cols*8 + 2*xpad, rows*18 + 2*ypad (gohufont 14 = 8x14 + 4 line spacing)
WIDTH, HEIGHT = COLS * 8 + 30, ROWS * 18 + 30
FPS = 12  # 32-frame loop -> ~2.7s per cycle

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
    base = compose(COLS, ROWS)
    t = gifos.Terminal(WIDTH, HEIGHT, 15, 15, font_size=15)
    t.set_fps(FPS)
    t.toggle_show_cursor(False)
    t.toggle_blink_cursor(False)

    # one full redraw per frame; only the texture cells differ between frames
    for f in range(LOOP_FRAMES):
        t.clear_frame()
        for r, row in enumerate(animate_texture(base, f)):
            t.gen_text(row_to_ansi(row), r + 1, count=0)
        t.gen_text("", ROWS, count=1, contin=True)  # emit the frame

    # gen_gif() always writes an infinitely looping gif, which is what an
    # ambient animation wants. The 32-frame cycle is seamless (see art.py).
    t.gen_gif()


if __name__ == "__main__":
    main()
