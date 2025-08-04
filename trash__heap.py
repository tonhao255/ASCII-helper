import keyboard as k
import time
import threading
import sys


# region Variables

# General settings
columns = 20
rows = 10
transparent = False

# Fps settings
fps = 4
spf = 1 / fps
curr_frame = 1

# Screen
screen = [[" " for _ in range(20)] for _ in range(10)]

# Cursor
x, y = 0, 0

# Selection and Buffer
select = False
selection = []
slct_x, slct_y = 0, 0
paste_buffer = []

# region Key processing

# Sets of keys simulating Gamemaker's keyboard functions
keyboard_check = set()
keyboard_check_pressed = set()
keyboard_check_released = set()

# Queue of raw events (thread-safe with lock)
event_queue = []
queue_lock = threading.Lock()

# endregion

# endregion

# region Functions

# region Key processing 2

# Function that is called by the hook
def on_key_event(event):
    with queue_lock:
        event_queue.append((event.name, event.event_type))

# Function that is called every frame
def process_events():
    global keyboard_check, keyboard_check_pressed, keyboard_check_released

    keyboard_check_pressed.clear()
    keyboard_check_released.clear()

    with queue_lock:
        events = list(event_queue)
        event_queue.clear()

    for name, event_type in events:
        if event_type == 'down':
            if name not in keyboard_check:
                keyboard_check_pressed.add(name)
                keyboard_check.add(name)
        elif event_type == 'up':
            if name in keyboard_check:
                keyboard_check_released.add(name)
                keyboard_check.remove(name)

# endregion

# Function to easen combos like ctrl + shift + v
def combo(mods: set[str], key: str):
    return mods <= keyboard_check and key in keyboard_check_pressed

# Printing board better
def print_board(screen, x, y, slct_x, slct_y, select, transparent):
    global curr_frame
    frame_lines = []

    # Top border
    frame_lines.append("+" + "-" * len(screen[0]) + "+")

    for row in range(len(screen)):
        line = "|"
        for column in range(len(screen[0])):
            cell = screen[row][column]
            colored = cell

            # Cursor
            if row == y and column == x:
                colored = "\033[91m" + ("." if cell == " " else cell) + "\033[0m"
            # Selection area
            elif select and min(y, slct_y) <= row <= max(y, slct_y) and min(x, slct_x) <= column <= max(x, slct_x):
                colored = "\033[92m" + ("." if cell == " " else cell) + "\033[0m"

            line += colored
        line += "|"
        frame_lines.append(line)

    # Bottom border
    frame_lines.append("+" + "-" * len(screen[0]) + "+")
    frame_lines.append(f"the cursor is at ({x}, {y})")
    frame_lines.append("Press ctrl + ? for help")
    frame_lines.append("Transparent pasting: " + ("On" if transparent else "Off"))
    frame_lines.append("frame: " + str(curr_frame))
    frame_lines.append(str(keyboard_check))

    curr_frame += 1
    if curr_frame > fps:
        curr_frame = 1

    # Join everything and print at once, moving cursor to top left
    print("\033[2J\033[H", end="")  # Clear screen and move cursor to top-left
    sys.stdout.write("\033[H" + "\n".join(frame_lines) + "\n")
    sys.stdout.flush()

# Moves cursor
def move_cursor(direction):
    global x, y
    if direction == "up" and y > 0:
        y -= 1
    elif direction == "down" and y < len(screen) - 1:
        y += 1
    elif direction == "left" and x > 0:
        x -= 1
    elif direction == "right" and x < len(screen[0]) - 1:
        x += 1

# Modify size of the screen
def screen_resize(index: int, dir: str, type: str):
    global screen

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

# endregion

# region Calls

k.hook(on_key_event) # Hook the keyboard event function

print("\033[2J", end="")  # Clear screen initially

print_board(screen, x, y, slct_x, slct_y, select, transparent) # Print the initial board

# endregion

# region Main loop
while True:
    # region Variables reset

    frame_start = time.perf_counter()

    # endregion
    
    # region Inital calls

    process_events()

    # endregion

    # region Main logic



    # endregion

    # region Final calls

    print_board(screen, x, y, slct_x, slct_y, select, transparent)
    
    # endregion

    # region Fps stabilizing
    elapsed = time.perf_counter() - frame_start
    time.sleep(max(0, spf - elapsed))
    # endregion

# endregion
