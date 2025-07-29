import keyboard as k
import os

rows = int(input("Rows: "))
columns = int(input("Columns: "))

most_common = ["_", "/", "\\", "|", "-"]

cmn_query = True if input("Modify most common characters? 0-> no, 1-> yes: ") == "1" else False

if cmn_query:
    most_common = []
    n = input("Type characters in order, nothing to exit: ")
    while n != "":
        if n not in most_common:
            most_common.append(n[0])
        n = input("Type characters in order, nothing to exit: ")
    if len(most_common) < 1:
        most_common = [" "]
    print("Exited")

screen = [[" " for _ in range(columns)] for _ in range(rows)]

x, y = 0, 0
type_mode = True
key_pressed = False
last = 0

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board():
    clear_terminal()
    print("+" + "-" * len(screen[0]) + "+")
    for row in range(len(screen)):
        print("|", end="")
        for column in range(len(screen[0])):
            if row == y and column == x:
                print("\033[91m", end="")  # Red color
                if screen[row][column] == " ":
                    print(".", end="")
                else:
                    print(screen[row][column], end="")
            else:
                print(screen[row][column], end="")
            print("\033[0m", end="")  # Reset color
        print("|")

    print("+" + "-" * len(screen[0]) + "+")

    print(f"the cursor is at ({x}, {y})")
    print("Use arrow keys to move, Enter to cycle through most common, Tab to enter/exit Type Mode (edit continuously), Esc to quit.")
    print("Type Mode: " + ("On" if type_mode else "Off"))

def copy_pasta():
    clear_terminal()
    for row in range(len(screen)):
        for column in range(len(screen[0])):
                print(screen[row][column], end="")
        print()

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

def mod_board(index: int, dir: str, type: str):

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

def keyboard_input(valid_keys: list[str], prompt: str = "") -> str:
    if prompt:
        print(prompt)

    while True:
        event = k.read_event()
        if event.event_type == k.KEY_DOWN and event.name.lower() in valid_keys:
            while True:
                up_event = k.read_event()
                if up_event.event_type == k.KEY_UP and up_event.name == event.name:
                    break
            return event.name


print_board()

modmap = {
    'ctrl': ['ctrl', 'left ctrl', 'right ctrl'],
    'alt': ['alt', 'alt gr', 'left alt', 'right alt'],
    'shift': ['shift', 'left shift', 'right shift'],
    'windows': ['windows', 'left windows', 'right windows']
}

while True:

    while True:
        event = k.read_event()

        if (event.event_type == k.KEY_DOWN) and (not key_pressed) and (event.name not in sum(modmap.values(), [])):
            mods = []

            for mod, aliases in modmap.items():
                if any(k.is_pressed(alias) for alias in aliases):
                    mods.append(mod)

            key_pressed = True
            break

        if event.event_type == k.KEY_UP:
            key_pressed = False
        continue

    key = event.name

    key = " " if key == "space" else key
    
    '''
    Current situation: 
    arrow keys = move cursor
    backspace = moves back and deletes character
    insert = new row/column
    delete = remove row/column
    enter = cycle through most common characters
    home = goes to start of row
    end = goes to end of row
    page up = goes to start of column
    page down = goes to end of column
    tab = type mode (goes to next character after typing)
    '''

    if len(key) == 1:
        screen[y][x] = key
        if type_mode:
            move_cursor("right")

    elif key == "backspace":
        screen[y][x] = " "
        move_cursor("left")

    elif key == "enter":
        screen[y][x] = most_common[last]
        last += 1
        if last >= len(most_common):
            last = 0

    elif key == "tab":
        type_mode = not type_mode

    elif key == "up" or key == "down" or key == "left" or key == "right":
        move_cursor(key)
    
    elif key == "home":
        x = 0
    
    elif key == "end":
        x = len(screen[0]) - 1

    elif key == "page up":
        y = 0
    
    elif key == "page down":
        y = len(screen) - 1

    elif key == "insert":
        dir = keyboard_input(["r" , "c", "e"], "Insert row (r) or column (c), or exit (e): ")

        if dir == "r":
            mod_board(y , "row" , "insert")            
        elif dir == "c":
            mod_board(x, "column" , "insert")
        elif dir == "e":
            pass
    
    elif key == "delete":
        dir = keyboard_input(["r" , "c", "e"], "Insert row (r) or column (c), or exit (e): ")

        if dir == "r":
            mod_board(y , "row" , "delete")
        elif dir == "c":
            mod_board(x, "column" , "delete")
        elif dir == "e":
            pass
    # if key == "esc":
    #     copy_pasta()
    #     break
    # elif edit_mode:

    #     key = " " if key == "space" else key

    #     if key == "enter":
    #         edit_mode = False
    #     elif key == "backspace":
    #         move_cursor("left")
    #         screen[y][x] = " "
    #     elif len(key) == 1:
    #         screen[y][x] = key
    #         if type_mode:
    #             move_cursor("right")
    #         else:
    #             edit_mode = False
    # elif key == "up":
    #     move_cursor("up")
    # elif key == "down":
    #     move_cursor("down")
    # elif key == "left":
    #     move_cursor("left")
    # elif key == "right":
    #     move_cursor("right")
    # elif key == "enter":
    #     edit_mode = True
    # elif key == "space":
    #     type_mode = not type_mode

    print_board()
    print(mods)
    print(event)
