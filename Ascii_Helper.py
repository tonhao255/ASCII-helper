import keyboard as k
import os
import pyperclip as p

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

# region
screen = [[" " for _ in range(columns)] for _ in range(rows)]

x, y = 0, 0
key_pressed = False
last = 0
select = False
selection = []
slct_x, slct_y = 0, 0
paste_buffer = []

transparent = False

messages = []
# endregion

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
            elif select and row >= min(y, slct_y) and row <= max(y, slct_y) and column >= min(x, slct_x) and column <= max(x, slct_x):
                print("\033[92m", end="")  # Green color
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
    print("Press ctrl + ? for help")
    print("Transparent pasting: " + ("On" if transparent else "Off"))
    print(k.all_modifiers)

def copy_pasta():
    string = ""
    for row in range(len(screen)):
        for column in range(len(screen[0])):
                string += screen[row][column]
        string += "\n"
    p.copy(string)
    global messages
    messages.append("\033[92mCurrent canvas copied and ready to paste\033[0m")

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
        event = k.read_event(suppress=True)
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
    messages = []

    try:
        while True:
        
            event = k.read_event()

            # arrow_keys = ["up", "down", "left", "right"]
            # pressed_arrows = [kname for kname in arrow_keys if k.is_pressed(kname)]

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
    except:
        pass

    key = event.name

    key = " " if key == "space" else key

    ################### DONE ###################
    if key == "esc":
        print("Program finished")
        break
    
    ################### DONE ###################
    if len(key) == 1 and ("ctrl" not in mods):
        screen[y][x] = key
        move_cursor("right")

    ################### DONE ###################
    elif key == "backspace":
        screen[y][x] = " "
        move_cursor("left")

    elif key == "enter":
        screen[y][x] = most_common[last]
        last += 1
        if last >= len(most_common):
            last = 0

    elif key == "tab":
        transparent = not transparent

    ################### DONE ###################
    elif key == "up" or key == "down" or key == "left" or key == "right":
        if mods == ["shift"]:
            if not select:
                slct_x, slct_y = x, y
                select = True
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
    
    elif key == "s" and ("ctrl" in mods):
        copy_pasta()

    elif key == "?" and ("ctrl" in mods):
        messages.append('''
Commands: 
arrow keys          = move cursor
backspace           = moves back and deletes character
insert              = new row/column
delete              = remove row/column
enter               = cycle through most common characters
home                = goes to start of row
end                 = goes to end of row
page up             = goes to start of column
page down           = goes to end of column
tab                 = toggle "transparent" pasting
ctrl + s            = save canvas to copy/paste buffer
shift + arrow keys  = select zone in canvas
ctrl + shift + c    = copy zone in canvas
ctrl + shift + v    = paste zone into canvas
ctrl + shift + x    = cut zone in canvas
ctrl + shift + d    = delete zone in canvas
ctrl + shift + del  = delete whole canvas
''')

    elif key.lower() == "c" and ("ctrl" in mods) and ("shift" in mods):
        paste_buffer = selection
        messages.append("\033[92mSelected region copied to program's clipboard\033[0m")
        select = False

    elif key.lower() == "v" and ("ctrl" in mods) and ("shift" in mods):
        for row in range(y, y + len(paste_buffer)):
            for col in range(x, x + len(paste_buffer[0])):
                if row < len(screen) and col < len(screen[0]):
                    if paste_buffer[row - y][col - x] != " ":
                        screen[row][col] = paste_buffer[row - y][col - x]
        messages.append("\033[92mSelection pasted successfully\033[0m")

    elif key.lower() == "x" and ("ctrl" in mods) and ("shift" in mods):
        paste_buffer = selection
        for row in range(min(y, slct_y), max(y, slct_y) + 1):
            screen[row][min(x, slct_x): max(x, slct_x) + 1] = [" "] * (max(x, slct_x) - min(x, slct_x) + 1)
        messages.append("\033[92mSelected region cut to program's clipboard\033[0m")
        select = False

    elif key.lower() == "d" and ("ctrl" in mods) and ("shift" in mods):
        for row in range(min(y, slct_y), max(y, slct_y) + 1):
            screen[row][min(x, slct_x): max(x, slct_x) + 1] = [" "] * (max(x, slct_x) - min(x, slct_x) + 1)
        messages.append("\033[92mSelected region deleted\033[0m")
        select = False

    ################### DONE ###################
    if key not in ["up", "down", "left", "right"] or "shift" not in mods:
        slct_x, slct_y = 0, 0
        select = False

    ################### DONE ###################
    if select:
        selection = []
        n = 0
        for i in range(min(y, slct_y), max(y, slct_y) + 1):
            selection.append([])
            for j in range(min(x, slct_x), max(x, slct_x) + 1):
                selection[n].append(screen[i][j])
            n += 1

    ################### WHAT WHY IS THIS ONE REPEATED BRUH ###################
    if key not in ["up", "down", "left", "right"] or "shift" not in mods:
        slct_x, slct_y = 0, 0
        select = False


    print_board()
    for i in messages:
        print(i)
    print(mods)
    print(event)
