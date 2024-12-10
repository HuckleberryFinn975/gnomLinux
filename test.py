import re
from mainClass import MainClass
log_file_path = "logOasis.txt"
keyPhrase = "text = ????????????? ñóìêè: "

with open(log_file_path, 'r', encoding="utf-8") as file:
    file = file.read()
position = file.rfind(keyPhrase)
if position != -1:
    print(f'  LOG 1 SUCCES {keyPhrase} found on position {position}')
    fullness = file[position + len(keyPhrase) : position + len(keyPhrase) + 2]
    print(f"    Fullness is {fullness}")
else:
    print("  Not Found | Search different unicode")
    pattern = r"text\s=\s[^\s]{13}\s[^\s]{5}:\s"
    matches = list(re.finditer(pattern, file))
    if matches:
        # Останній збіг
        last_match = matches[-1]
        print("Знайдено! Індекс початку з кінця:", last_match.start())
        print("Patern found", last_match.group())
        position = last_match.start()
        fullness = file[position + len(keyPhrase) : position + len(keyPhrase) + 2]
        print(f"    Fullness is {fullness}")

    else:
        print("Patern not found")
        print(f"  different unicode also not found")
