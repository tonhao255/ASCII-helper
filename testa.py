alias = {
        "ctrl":     ["ctrl", "right ctrl", "left ctrl"],
        "shift":    ["shift", "left shift", "right shift"],
        "alt":      ["alt", "right alt", "left alt", "alt gr"],
        "windows":  ["windows", "left windows", "right windows"],
    }

def check_mods(mods: list[str]):
    result = True
    for mod in mods:
        if set(alias[mod]).intersection(set("left ctrl")):
            result = False
    return result

select_set = [item for sublist in list(alias.values()) for item in sublist]
select_set.extend(["up", "down", "left", "right"])
print(check_mods(["ctrl"]))
print([item for sublist in list(alias.values()) for item in sublist])
print(select_set)

'''
═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬

╒ ╓ ╕ ╖ ╘ ╙ ╛ ╜ ╞ ╟ ╡ ╢ ╤ ╥ ╧ ╨ ╪ ╫ 

─ ━ 
│ ┃ 
┄ ┅ 
┆ ┇ 
┈ ┉ 
┊ ┋ 

┌ ┍ ┎ ┏ 
┐ ┑ ┒ ┓ 

└ ┕ ┖ ┗ 
┘ ┙ ┚ ┛ 

├ ┝ ┞ ┟ ┠ ┡ ┢ ┣ 

┤ ┥ ┦ ┧ ┨ ┩ ┪ ┫ 

┬ ┭ ┮ ┯ ┰ ┱ ┲ ┳ 

┴ ┵ ┶ ┷ ┸ ┹ ┺ ┻ 

┼ ┽ ┾ ┿ ╀ ╁ ╂ ╃ ╄ ╅ ╆ ╇ ╈ ╉ ╊ ╋ 

╌ ╍ 
╎ ╏ 

═ ║ 
╒ ╓ ╔ 
╕ ╖ ╗ 
╘ ╙ ╚ 
╛ ╜ ╝ 
╞ ╟ ╠ 
╡ ╢ ╣ 
╤ ╥ ╦ 
╧ ╨ ╩ 
╪ ╫ ╬ 

╭ ╮ ╯ ╰	╱ ╲ ╳ ╴ ╵ ╶ ╷ ╸ ╹ ╺ ╻ ╼ ╽ ╾ ╿

'''