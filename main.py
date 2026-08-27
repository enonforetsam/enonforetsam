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

    # --- fake BIOS boot ---
    t.gen_text("", 1, count=15)
    t.toggle_show_cursor(False)
    year_now = datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).strftime("%Y")
    t.gen_text("THE MASTER LAB -- Modular BIOS v1.0", 1)
    t.gen_text(f"Copyright (C) {year_now}, \x1b[35mKrackedDevs Studio\x1b[0m", 2)
    t.gen_text("\x1b[94mGitHub Profile Terminal, Rev 1\x1b[0m", 4)
    t.gen_text("KualaLumpur(tm) GIFCPU - 100Hz", 6)
    t.gen_text(
        "Press \x1b[94mDEL\x1b[0m to enter SETUP, \x1b[94mESC\x1b[0m to cancel Memory Test",
        t.num_rows,
    )
    for i in range(0, 65653, 9216):
        t.delete_row(7)
        t.gen_text(f"Memory Test: {i}", 7, count=1, contin=True)
    t.delete_row(7)
    t.gen_text("Memory Test: 64KB OK", 7, count=8, contin=True)
    t.gen_text("", 11, count=8, contin=True)

    t.clear_frame()
    t.gen_text("Initiating Boot Sequence ", 1, contin=True)
    t.gen_typing_text(".....", 1, contin=True)
    t.gen_text("", 1, count=6, contin=True)

    mid_row = (t.num_rows + 1) // 2
    box_lines = [
        r"+-- THE MASTER LAB -----------------+",
        r"|  master of none, builder of KL    |",
        r"+------------------------------------+",
    ]
    for i, line in enumerate(box_lines):
        t.gen_text(f"\x1b[95m{line}\x1b[0m", mid_row - 1 + i, 10, count=3, contin=True)
    t.gen_text("", t.num_rows, count=10, contin=True)

    # --- login screen ---
    t.clear_frame()
    t.clone_frame(4)
    t.toggle_show_cursor(False)
    t.gen_text("\x1b[93mTHE MASTER LAB v1.0 (tty1)\x1b[0m", 1, count=4)
    t.gen_text("login: ", 3, count=4)
    t.toggle_show_cursor(True)
    t.gen_typing_text(USER, 3, contin=True)
    t.gen_text("", 4, count=4)
    t.toggle_show_cursor(False)
    t.gen_text("password: ", 4, count=4)
    t.toggle_show_cursor(True)
    t.gen_typing_text("*********", 4, contin=True)
    t.toggle_show_cursor(False)
    time_now = datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).strftime(
        "%a %b %d %I:%M:%S %p %Z %Y"
    )
    t.gen_text(f"Last login: {time_now} on tty1", 6)

    # MOTD: block-letter banner, rows 8-18
    for i, line in enumerate(BANNER):
        t.gen_text(f"\x1b[95m{line}\x1b[0m", 8 + i, count=0)
    t.gen_text("", 8, count=6, contin=True)

    prompt_row = 8 + len(BANNER) + 1
    t.gen_prompt(prompt_row, count=4)
    prompt_col = t.curr_col
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[91mclea", prompt_row, contin=True)
    t.delete_row(prompt_row, prompt_col)
    t.gen_text("\x1b[92mclear\x1b[0m", prompt_row, count=2, contin=True)

    # --- fetch real GitHub stats ---
    git = gifos.utils.fetch_github_stats(USER)
    top_languages = [lang[0] for lang in git.languages_sorted]

    t.clear_frame()
    t.gen_prompt(1)
    prompt_col = t.curr_col
    t.clone_frame(8)
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[91mfetch.s", 1, contin=True)
    t.delete_row(1, prompt_col)
    t.gen_text("\x1b[92mfetch.sh\x1b[0m", 1, contin=True)
    t.gen_typing_text(f" -u {USER}", 1, contin=True)
    t.toggle_show_cursor(False)

    details = f"""
    \x1b[30;105m{USER}@GitHub\x1b[0m
    --------------
    \x1b[96mRole:    \x1b[93mbuilder - jack of all trades, master of none\x1b[0m
    \x1b[96mBase:    \x1b[93mKuala Lumpur, Malaysia\x1b[0m
    \x1b[96mStudio:  \x1b[94mkrackeddevs.com\x1b[0m
    \x1b[96mSite:    \x1b[94mthemasterofnone.xyz\x1b[0m

    \x1b[30;105mGitHub Stats\x1b[0m
    --------------
    \x1b[96mUser Rating:         \x1b[93m{git.user_rank.level}\x1b[0m
    \x1b[96mTotal Stars Earned:  \x1b[93m{git.total_stargazers}\x1b[0m
    \x1b[96mCommits ({int(year_now) - 1}):       \x1b[93m{git.total_commits_last_year}\x1b[0m
    \x1b[96mTotal PRs:           \x1b[93m{git.total_pull_requests_made}\x1b[0m
    \x1b[96mMerged PR %:         \x1b[93m{git.pull_requests_merge_percentage}\x1b[0m
    \x1b[96mRepo Contributions:  \x1b[93m{git.total_repo_contributions}\x1b[0m
    \x1b[96mTop Languages:       \x1b[93m{', '.join(top_languages[:5])}\x1b[0m
    """
    t.gen_text(details, 2, 3, count=4, contin=True)
    t.gen_prompt(t.curr_row)
    t.toggle_show_cursor(True)
    t.gen_typing_text(
        "\x1b[92m# building in public, one experiment at a time",
        t.curr_row,
        contin=True,
    )
    t.gen_text("", t.curr_row, count=100, contin=True)

    t.gen_gif()


if __name__ == "__main__":
    main()
