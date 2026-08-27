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
STEP_X, STEP_Y = 11, 4  # per-letter diagonal step (right, up)


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
    word_left = (cols - total_w) // 2 + 1
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

    # --- footer tags set into the bottom edge, like the reference's ".xxxx: 1981" ---
    tag_l = " enonforetsam "
    tag_r = " .xxxx: KL 2026 "
    _blit(grid, [tag_l], bot, lft + 3, "tag", keep_spaces=True)
    _blit(grid, [tag_r], bot, rgt - 3 - len(tag_r), "tag", keep_spaces=True)

    return grid


def to_plain(grid):
    return "\n".join("".join(ch for ch, _ in row).rstrip() for row in grid)


if __name__ == "__main__":
    import sys

    cols = int(sys.argv[1]) if len(sys.argv) > 1 else 76
    rows = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    print(to_plain(compose(cols, rows)))
