import curses

def main(stdscr):
    curses.start_color()  # <- Required before using color pairs
    curses.use_default_colors()  # Allows transparency with -1

    # Use color IDs 0–7. For example, RED on default background:
    curses.init_pair(1, curses.COLOR_RED, -1)

    stdscr.clear()
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, 0, "This is red text.")
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)
