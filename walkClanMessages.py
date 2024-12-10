import pyautogui
from pyautogui import click
from time import sleep
pyautogui.FAILSAFE = False

log_file_path = "logOasis.txt"

with open(log_file_path, 'r') as file:
    file = file.read()
endingIndex = len(file)

def rightSoft():
    click(850, 930)
def leftSoft():
    click(450, 930)

def clMessageCheck(keyPhrase = "server -> client: 18"):
    global endingIndex
    with open(log_file_path, 'r') as file:
        file = file.read()
    position = file.find(keyPhrase, endingIndex)
    if position != -1:
        endingIndex = position + len(keyPhrase)
        print("\t\tCLAN_MESS INTERTAL PROCESS")
        leftSoft()
        return True
    else:
        return False

print(f"LOOP STARTED from index: {endingIndex}")

while True:
	clMessageCheck()
	sleep(.15)