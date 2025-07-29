import keyboard as k
import os

rows = int(input("Linhas: "))
columns = int(input("Colunas: "))

screen = [[" " for _ in range(columns)] for _ in range(rows)]

x, y = 0, 0
edit_mode = False
type_mode = False
key_pressed = False

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board():
    clear_terminal()
    print("+" + "-" * columns + "+")
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

    print("+" + "-" * columns + "+")

    print(f"Cursor está na posição {x}, {y}")
    if edit_mode:
        print("\033[0;32mEdit mode: press a key to write into the cell.\033[0m")
    print("Use arrow keys to move, Enter to edit, Space out of edit to enter/exit Type Mode (edit continuously) Esc to quit.")
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

print_board()

nono_events = ["left shift", "right shift" , "left ctrl" , "right ctrl", "alt" , "alt gr"]

while True:

    while True:
        event = k.read_event()
        if event.event_type == k.KEY_DOWN and (event.name not in nono_events) and not key_pressed:
            key_pressed = True
            break
        if event.event_type == k.KEY_UP:
            key_pressed = False
        continue

    key = event.name

    if key == "esc":
        copy_pasta()
        break
    elif edit_mode:

        key = " " if key == "space" else key

        if key == "enter":
            edit_mode = False
        elif key == "backspace":
            move_cursor("left")
            screen[y][x] = " "
        elif len(key) == 1:
            screen[y][x] = key
            if type_mode:
                move_cursor("right")
            else:
                edit_mode = False
    elif key == "up":
        move_cursor("up")
    elif key == "down":
        move_cursor("down")
    elif key == "left":
        move_cursor("left")
    elif key == "right":
        move_cursor("right")
    elif key == "enter":
        edit_mode = True
    elif key == "space":
        type_mode = not type_mode

    print_board()
    print(event)
