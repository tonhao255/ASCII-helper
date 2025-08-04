import curses
import keyboard as k
import threading
import time

def main(terminal):
    # Initialization
    curses.curs_set(0)  # Hide cursor
    curses.start_color()
    curses.use_default_colors()

    # Init color pairs
    curses.init_pair(1, curses.COLOR_RED, -1)    # Cursor red
    curses.init_pair(2, curses.COLOR_GREEN, -1)  # Selection green

      
    # Sets of keys simulating Gamemaker"s keyboard functions
    keyboard_check = set()
    keyboard_check_pressed = set()
    keyboard_check_released = set()    
    keys_to_remove = set()
    key_cooldowns = {}  # key: frames left to wait before re-adding
    COOLDOWN_FRAMES = 2

    log_path = "input_log.txt"
    last_logged_line = None
    repeat_count = 0
    log_file = open(log_path, "w", encoding="utf-8")

    # aliases = {"right ctrl": "ctrl",
    #            "right alt": "alt",
    #            "left windows": "windows",
    #            "right windows": "windows",
    #            "left alt": "alt",
    #            "left ctrl": "ctrl",
    #            "left shift": "shift",
    #            "right shift": "shift",
    #            "alt gr": "alt"}
    
    alias = {
        "ctrl":     ["ctrl", "right ctrl", "left ctrl"],
        "shift":    ["shift", "left shift", "right shift"],
        "alt":      ["alt", "right alt", "left alt", "alt gr"],
        "windows":  ["windows", "left windows", "right windows"],
    }
    select_set = [item for sublist in list(alias.values()) for item in sublist]
    select_set.extend(["up", "down", "left", "right"])

    # Queue of raw events (thread-safe with lock)
    event_queue = []
    queue_lock = threading.Lock()

    # Fps settings
    fps = 10
    spf = 1 / fps
    curr_frame = 1
    estimate_fps = 0
    elapsed = 0
    
    # Initialize screen
    rows, columns = 10, 20
    screen = [[" " for _ in range(columns)] for _ in range(rows)]
    
    # Cursor and selection
    x, y = 0, 0
    select = False
    selection = []
    slct_x, slct_y = 0, 0
    paste_buffer = []

    # Box keys
    # box_keys =      ["═", "║", "╔" ,"╗" ,"╚", "╝", "╠", "╣", "╦", "╩", "╬"]
    # box_keys_alt =  ["╒", "╓", "╕", "╖", "╘", "╙", "╛", "╜", "╞", "╟", "╡", "╢", "╤", "╥", "╧", "╨", "╪", "╫"]
    # last_box_key = 0
    # last_box_key_alt = 0
    all_box_characters = {
        "thin":             ["─","│","┌","┐","└","┘","├","┤","┬","┴","┼"],
        "thick":            ["━","┃","┏","┓","┗","┛","┣","┫","┳","┻","╋"],
        "double":           ["═","║","╔","╗","╚","╝","╠","╣","╦","╩","╬"],
        "cut":              ["╌","╍","╎","╏","┄","┅","┆","┇","┈","┉","┊","┋"],
        "thin-thick":       ["┍","┎","┑","┒","┕","┖","┙","┚",
                             "┝","┞","┟","┠","┡","┢",
                             "┥","┦","┧","┨","┩","┪",
                             "┭","┮","┯","┰","┱","┲",
                             "┵","┶","┷","┸","┹","┺",
                             "┽","┾","┿","╀","╁","╂","╃","╄","╅","╆","╇","╈","╉","╊",
                             "╼","╽","╾","╿"],
        "single-double":    ["╒","╓","╕","╖","╘","╙","╛","╜","╞","╟","╡","╢","╤","╥","╧","╨","╪","╫"],
        "curves-diagonals": ["╭","╮","╯","╰	╱","╲","╳"],
        "terminations":     ["╴","╵","╶","╷","╸","╹","╺","╻"]
    }

    # Settings
    transparent = False
    at_stt = False

    # Main board printing function
    def print_board_curses():
        terminal.clear()
        rows = len(screen)
        cols = len(screen[0])

        # Top border
        terminal.addstr(0, 0, "┌" + "─" * (cols) + "┐")

        for row in range(rows):
            terminal.addstr(row + 1, 0, "│")  # Left border

            for col in range(cols):
                ch = screen[row][col]
                color = curses.color_pair(0)

                if row == y and col == x:
                    color = curses.color_pair(1)  # Red: Cursor
                elif select and min(y, slct_y) <= row <= max(y, slct_y) and min(x, slct_x) <= col <= max(x, slct_x):
                    color = curses.color_pair(2)  # Green: Selection

                to_print = "." if ch == " " and color != curses.color_pair(0) else ch
                terminal.addstr(row + 1, col + 1, to_print, color)

            terminal.addstr(row + 1, cols + 1, "│")  # Right border

        # Bottom border
        terminal.addstr(rows + 1, 0, "└" + "─" * (cols) + "┘")

        # Info panel
        info_y = rows + 3
        terminal.addstr(info_y, 0,   f"📍 Cursor:        ({x}, {y})")
        terminal.addstr(info_y + 1, 0, f"🎨 Transparent:   {"On" if transparent else "Off"}")
        terminal.addstr(info_y + 2, 0, f"📦 Selection:     {[keyboard_check, keyboard_check_pressed, keyboard_check_released]}")
        terminal.addstr(info_y + 3, 0, f"🕒 FPS:           {estimate_fps}")
        terminal.addstr(info_y + 4, 0, f"📝 Message:       {key_cooldowns}")
        terminal.addstr(info_y + 5, 0, f"📝 Selection:     {selection}")
        terminal.addstr(info_y + 6, 0, f"{any(i in ["up", "down", "left", "right"] for i in keyboard_check) and not check_mods("shift")} {(not keyboard_check <= set(select_set))}")

        terminal.refresh()

    # Function that is called by the hook
    def on_key_event(event):
        with queue_lock:
            event_queue.append((event.name, event.event_type))

    # Function that is called every frame
    def process_events():
        nonlocal keyboard_check, keyboard_check_pressed, keyboard_check_released, key_cooldowns

        # Step 1: Apply removals from fast key taps
        for key in keys_to_remove:
            keyboard_check.discard(key)
            if key in key_cooldowns:
                del key_cooldowns[key]
        keys_to_remove.clear()

        keyboard_check_pressed.clear()
        keyboard_check_released.clear()

        with queue_lock:
            events = list(event_queue)
            event_queue.clear()

        # Step 2: Process new input events
        for name, event_type in events:
            if event_type == "down":
                if (name not in keyboard_check and
                    name not in key_cooldowns):
                    keyboard_check_pressed.add(name)
                    keyboard_check.add(name)

            elif event_type == "up":
                if name in keyboard_check:
                    keyboard_check_released.add(name)
                    if name in keyboard_check_pressed:
                        # Pressed and released in the same frame? Delay removal.
                        keys_to_remove.add(name)
                    else:
                        keyboard_check.remove(name)

                if name in key_cooldowns:
                    del key_cooldowns[name]

        # Step 4: Countdown cooldowns
        for key in list(key_cooldowns):
            key_cooldowns[key] -= 1
            if key in keyboard_check:
                keyboard_check.remove(key)
            if key_cooldowns[key] < 0:
                # Re-add if still being held (not released)
                keyboard_check.add(key)
                del key_cooldowns[key]

        for key in list(keyboard_check_pressed):
            if key not in keyboard_check_released and key not in list(k.all_modifiers):
                key_cooldowns[key] = COOLDOWN_FRAMES
        
        # to_del = []
        # for key, _ in key_cooldowns.items():
        #     key_cooldowns[key] -= 1
        #     if key in keyboard_check:
        #         keyboard_check.remove(key)
        #     if key_cooldowns[key] == 0:
        #         to_del.append(key)
        
        # for key in to_del:
        #     del key_cooldowns[key]
        
        # for key in keyboard_check_pressed:
        #     key_cooldowns[key] = COOLDOWN_FRAMES
        # Step 4: Handle cooldowns
        # to_readd = []
        # for key, frames_left in key_cooldowns.items():
        #     if frames_left == -1:
        #         key_cooldowns[key] = COOLDOWN_FRAMES
        #     elif frames_left == COOLDOWN_FRAMES:
        #         keyboard_check.discard(key)  # Remove for cooldown next frame
        #         key_cooldowns[key] -= 1
        #     else:
        #         key_cooldowns[key] -= 1
        #         if key_cooldowns[key] <= 0:
        #             to_readd.append(key)

        # for key in to_readd:
        #     if key not in keys_to_remove:  # Only re-add if not released
        #         keyboard_check.add(key)

    # Cursor movment
    def move_cursor(direction):
        nonlocal x, y, screen

        if direction == "up" and y > 0:
            y -= 1
        elif direction == "down" and y < len(screen) - 1:
            y += 1
        elif direction == "left" and x > 0:
            x -= 1
        elif direction == "right" and x < len(screen[0]) - 1:
            x += 1

    # Screen resizing
    def screen_resize(index: int, dir: str, type: str):
        nonlocal rows, columns, screen
        if dir == "row":
            if index < len(screen):
                if type == "insert":
                    screen.insert(index + 1 , [" " for _ in range(columns)])

                elif type == "delete":
                    del screen[index]

        elif dir == "column":
            if index < len(screen[0]):
                if type == "insert":
                    for row in range(len(screen)):
                        screen[row].insert(index + 1 , " ")
                elif type == "delete":
                    for row in range(len(screen)):
                        del screen[row][index]

    # Function that examines modifications like shift, ctrl, alt
    def check_mods(*mods):
        nonlocal keyboard_check, alias
        result = True
        for mod in mods:
            if not set(alias[mod]).intersection(keyboard_check):
                result = False
        return result

    # Function to easen combos like ctrl + shift + v
    def combo(mods: set[str], key: str):
        nonlocal keyboard_check_pressed
        return check_mods(*mods) and key in keyboard_check_pressed

    k.hook(on_key_event) # Hook the keyboard event function

    # Main loop
    while True:
        process_events()

        frame_start = time.perf_counter()

        if not at_stt:
            print_board_curses()

        if "esc" in keyboard_check:
            break
        
        if not check_mods("ctrl"):
            for i in keyboard_check:
                if i == "space":
                    i = " "

                if len(i) == 1:
                    screen[y][x] = i
                    move_cursor("right")

                if i in ["up", "down", "left", "right"]:
                    if check_mods("shift") and  not select:
                        slct_x, slct_y = x, y
                        select = True
                    move_cursor(i)

            if "enter" in keyboard_check_pressed:
                # if not check_mods("shift"):
                #     screen[y][x] = box_keys[last_box_key]
                # else:
                #     screen[y][x] = box_keys_alt[last_box_key_alt]
                pass

            if "tab" in keyboard_check_pressed:
                # last_box_key += 1
                # last_box_key_alt += 1
                # if last_box_key >= len(box_keys):
                #     last_box_key = 0
                # if last_box_key_alt >= len(box_keys_alt):
                #     last_box_key_alt = 0
                pass

            if "backspace" in keyboard_check:
                screen[y][x] = " "
                move_cursor("left")
        



        # region Selection
        if (any(i in ["up", "down", "left", "right"] for i in keyboard_check) and not check_mods("shift")) or (not keyboard_check <= set(select_set)):
            # slct_x, slct_y = 0, 0
            select = False
        
        if select:
            selection = []
            n = 0
            for i in range(min(y, slct_y), max(y, slct_y) + 1):
                selection.append([])
                for j in range(min(x, slct_x), max(x, slct_x) + 1):
                    selection[n].append(screen[i][j])
                n += 1
        # endregion

        # region Logger
        k_check = keyboard_check
        k_pressed = keyboard_check_pressed
        k_released = keyboard_check_released

        # Format the line
        current_line = f"[{sorted(k_check)} | {sorted(k_pressed)} | {sorted(k_released)}]"

        # Check for repetition
        if current_line == last_logged_line:
            repeat_count += 1
        else:
            if last_logged_line is not None:
                if repeat_count > 1:
                    log_file.write(f"{last_logged_line} x{repeat_count}\n")
                else:
                    log_file.write(f"{last_logged_line}\n")
            repeat_count = 1
            last_logged_line = current_line
        # endregion

        # region
        elapsed = time.perf_counter() - frame_start
        curr_frame += 1
        if curr_frame > fps:
            curr_frame = 1
        time.sleep(max(0, spf - elapsed))
        elapsed = time.perf_counter() - frame_start
        estimate_fps = round(1/max(elapsed, 0.001), 2)
        # endregion

if __name__ == "__main__":
    curses.wrapper(main)
