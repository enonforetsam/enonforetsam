"""ANSI-art compositor: MASTER climbing a diagonal in isometric letters, over a
dot-texture field, inside a line-art frame. Demoscene / BBS style.

compose() returns a grid of (char, cls) cells. cls is one of:
  "bg" (empty), "frame", "tex" (texture), "word" (big letters),
  "sub" (small OF NONE), "tag" (footer tags)
Everything is plain ASCII: the terminal's bitmap font is latin-1 only.
"""

import pyfiglet

WORD = "MASTER"
SUB = "OF NONE"
WORD_FONT = "isometric1"
SUB_FONT = "small"
STEP_X, STEP_Y = 13, 2  # per-letter diagonal step (right, up); flat enough for a 30-row landscape
INFO = [
    "enonforetsam",
    "kuala lumpur, my",
    "themasterofnone.xyz",
    "krackeddevs.com",
]


def _figlet_lines(text, font):
    lines = [l.rstrip() for l in pyfiglet.figlet_format(text, font=font).splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def _blit(grid, lines, top, left, cls, halo=0, clear=("tex", "bg"), keep_spaces=False):
    """Draw lines onto grid at (top, left). halo>0 blanks that many cells of
    padding around every glyph cell (only cells whose cls is in `clear`) so
    the glyph reads over whatever is underneath."""
    rows, cols = len(grid), len(grid[0])
    if halo:
        for r, line in enumerate(lines):
            for c, ch in enumerate(line):
                if ch == " ":
                    continue
                for dr in range(-halo, halo + 1):
                    for dc in range(-halo, halo + 1):
                        rr, cc = top + r + dr, left + c + dc
                        if 0 <= rr < rows and 0 <= cc < cols and grid[rr][cc][1] in clear:
                            grid[rr][cc] = (" ", "bg")
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            rr, cc = top + r, left + c
            if not (0 <= rr < rows and 0 <= cc < cols):
                continue
            if ch == " ":
                if keep_spaces:
                    grid[rr][cc] = (" ", "bg")
                continue
            grid[rr][cc] = (ch, cls)


def _hash(r, c):
    return ((r * 73856093) ^ (c * 19349663) ^ 0x5BD1E995) % 100


def compose(cols, rows):
    grid = [[(" ", "bg") for _ in range(cols)] for _ in range(rows)]

    # --- texture field: continuous vertical dotted runs, lens-shaped so the
    # field is tallest in the middle and tapers toward the side frames ---
    mid = rows / 2
    half = rows / 2 - 4
    for c in range(5, cols - 5):
        if c % 2:
            continue
        dist = abs(c - cols / 2) / (cols / 2)  # 0 centre .. 1 edge
        span = half * (1.0 - 0.3 * dist * dist)  # shallow lens: corners still get texture
        jit_top, jit_bot = _hash(1, c) % 5, _hash(2, c) % 5
        r0 = max(3, int(mid - span) + jit_top)
        r1 = min(rows - 4, int(mid + span) - jit_bot)
        for r in range(r0, r1 + 1):
            ch = ":" if (r + c // 2) % 2 == 0 else "'"
            grid[r][c] = (ch, "tex")
    # second, sparser layer on the odd columns through the middle band so the
    # centre packs tighter than the edges (reference has a dense core)
    for c in range(7, cols - 7):
        if c % 2 == 0:
            continue
        dist = abs(c - cols / 2) / (cols / 2)
        if dist > 0.6:
            continue
        for r in range(6, rows - 6):
            if (r + _hash(0, c)) % 3 == 0:
                grid[r][c] = (".", "tex")

    # --- frame: chamfered box + X chain inside left/right edges ---
    top, bot, lft, rgt = 0, rows - 1, 0, cols - 1
    for c in range(lft + 2, rgt - 1):
        grid[top][c] = ("_", "frame")
        grid[bot][c] = ("_", "frame")
    for r in range(top + 2, bot - 1):
        grid[r][lft] = ("|", "frame")
        grid[r][rgt] = ("|", "frame")
    grid[top + 1][lft] = ("/", "frame")
    grid[top + 1][lft + 1] = ("'", "frame")
    grid[top + 1][rgt] = ("\\", "frame")
    grid[top + 1][rgt - 1] = ("`", "frame")
    grid[bot - 1][lft] = ("\\", "frame")
    grid[bot - 1][lft + 1] = (".", "frame")
    grid[bot - 1][rgt] = ("/", "frame")
    grid[bot - 1][rgt - 1] = (",", "frame")
    for r in range(4, rows - 4):
        if r % 9 in (0, 1):  # gaps so the chain reads as ornament
            continue
        grid[r][lft + 2] = ("X", "frame")
        grid[r][rgt - 2] = ("X", "frame")
    # X-chain block hugging the top-left inside corner, like the reference's
    # ",XXXXXXXXXXXX:" header ornament
    _blit(grid, [",xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:", "xxxxxxxxxxxxxxxxxxx::"], top + 2, lft + 3, "frame", halo=1)

    # --- the word, stair-stepped up and to the right; later letters sit in front ---
    letters = [_figlet_lines(ch, WORD_FONT) for ch in WORD]
    letter_h = max(len(l) for l in letters)
    n = len(letters)
    total_h = letter_h + STEP_Y * (n - 1)
    total_w = STEP_X * (n - 1) + max(max(len(x) for x in l) for l in letters)
    word_top = (rows - total_h) // 2 - 1
    word_left = lft + 8  # anchored left; the right third is for the signature block
    for i, lines in enumerate(letters):
        t = word_top + STEP_Y * (n - 1 - i)
        l = word_left + STEP_X * i
        _blit(grid, lines, t, l, "word", halo=1)

    # --- OF NONE in the empty bottom-right ---
    sub = _figlet_lines(SUB, SUB_FONT)
    sub_w = max(len(x) for x in sub)
    sub_top = word_top + total_h - len(sub) + 1
    sub_left = cols - 5 - sub_w
    _blit(grid, sub, sub_top, sub_left, "sub", halo=1)

    # --- small info block stacked above OF NONE, sharing its right edge ---
    info_w = max(len(s) for s in INFO)
    info_left = sub_left + sub_w - info_w
    info_top = sub_top - len(INFO) - 1
    for i, s in enumerate(INFO):
        _blit(grid, [s.rjust(info_w)], info_top + i, info_left, "tag", halo=1, keep_spaces=True)

    # --- footer tags set into the bottom edge, like the reference's ".xxxx: 1981" ---
    tag_l = " enonforetsam "
    tag_r = " .xxxx: KL 2026 "
    _blit(grid, [tag_l], bot, lft + 3, "tag", keep_spaces=True)
    _blit(grid, [tag_r], bot, rgt - 3 - len(tag_r), "tag", keep_spaces=True)

    return grid


# --- animation: the texture field drifts downward like rain, with parallax ---
# Each texture column scrolls an 8-row pattern at one of three speeds. The loop
# is seamless when every column returns to its start: LCM(8*1, 8*2, 8*4) = 32.
PERIOD = 8
PATTERN = [":", "'", ".", " ", ":", " ", ".", " "]          # even columns (dense)
PATTERN_SPARSE = [".", " ", " ", " ", " ", ":", " ", " "]   # odd columns (the centre layer)
SPEEDS = (1, 2, 4)  # frames per one-row step
LOOP_FRAMES = PERIOD * max(SPEEDS)


def animate_texture(base, frame):
    """Return a copy of `base` with every 'tex' cell's glyph re-derived for
    `frame`. Only cells that are texture in the base grid ever change, so the
    word, frame, text and the halos around them stay put."""
    rows, cols = len(base), len(base[0])
    out = [row[:] for row in base]
    for c in range(cols):
        k = SPEEDS[_hash(3, c) % len(SPEEDS)]
        phase = _hash(4, c) % PERIOD
        pat = PATTERN if c % 2 == 0 else PATTERN_SPARSE
        off = frame // k
        for r in range(rows):
            if base[r][c][1] != "tex":
                continue
            ch = pat[(r - off + phase) % PERIOD]
            out[r][c] = (ch, "tex") if ch != " " else (" ", "bg")
    return out


def to_plain(grid):
    return "\n".join("".join(ch for ch, _ in row).rstrip() for row in grid)


if __name__ == "__main__":
    import sys

    cols = int(sys.argv[1]) if len(sys.argv) > 1 else 106
    rows = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    print(to_plain(compose(cols, rows)))
