import time
import requests
from mss import mss
from PIL import Image
from mainClass import MainClass
import os
import signal

def stopScript(process_id):
    os.kill(process_id, signal.SIGSTOP)
def resumeScript(process_id):
    os.kill(process_id, signal.SIGCONT)

targetColor = (255, 204, 0)
backgroundColor = (70, 70, 70)

tgApiGetUp = f'https://api.telegram.org/bot{MainClass.token1}/getUpdates'

def get_telegram_updates(offset = None):
    try:
        response = requests.get(
            tgApiGetUp,
            params={'timeout': 10, 'offset': offset}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Updates getting Error: {e}")
    return None
def wait_for_user_response(timeout = 600):
    end_time = time.time() + timeout
    last_update_id = None
    updates = get_telegram_updates()
    if updates and updates.get('result'):
        last_update_id = updates['result'][-1]['update_id'] + 1
    while time.time() < end_time:
        updates = get_telegram_updates(last_update_id)
        if updates and updates.get('result'):
            for update in updates['result']:
                last_update_id = update['update_id'] + 1
                if 'message' in update and 'text' in update['message']:
                    if update['message']['text'].upper() == 'Y':
                        return "YES"
                    elif update['message']['text'].upper() == 'N':
                        return "NO"
                    else:
                        return "Unrecognized"
        time.sleep(5)
    print("Response timed out")
    return "TiU"
def checkPixel(tarColor, backColor):
    bbox = {"top": 650, "left": 0, "width": 1280, "height": 300}

    with mss() as sct:
        screenshot = sct.grab(bbox)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

    pixels = img.load()
    width, height = screenshot.size

    for x in range(width):
        for y in range(0, height):
            if pixels[x, y] == tarColor and any(
            pixels[x + dx, y + dy] == backColor
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]
            if 0 <= x + dx < width and 0 <= y + dy < height
            ):
                print("See an incoming SMS")
                return True
    print("Don't see incoming messages")
    return False

def main():
    MainClass.send_message("Run LS Traker", MainClass.token2)    
    while True:
        if checkPixel(targetColor, backgroundColor):
            MainClass.send_message("A new message has been received. Stop script?  y/n", MainClass.token1, timeOut = MainClass.to1)
            for k in range(3):
                response = wait_for_user_response()
                if response == 'YES':
                    with open("./game.pid", "r") as f:
                        pid = int(f.read().strip())
                    stopScript(pid)
                    MainClass.send_message("The script has been paused. | Resume?  y/n", MainClass.token1, timeOut = MainClass.to1)
                    for i in range(3):
                        response = wait_for_user_response()
                        if response == "YES":
                            resumeScript(pid)
                            MainClass.send_message("The script was continued", MainClass.token1, timeOut = MainClass.to1)
                            time.sleep(8)
                            break
                        elif response == 'NO':
                            MainClass.send_message("The script was not continued", MainClass.token1, timeOut = MainClass.to1)
                            time.sleep(8)
                            break
                        elif response == 'Unrecognized':
                            MainClass.send_message(f"Your answer is not recognized({i+1}). Write again. y/n", MainClass.token1, timeOut = MainClass.to1)
                            continue
                        elif response == 'TiU':
                            MainClass.send_message("Response timed out. Exit", MainClass.token1, timeOut = MainClass.to1)
                            return 
                    break    
                elif response == 'NO':
                    MainClass.send_message("The script does not stop", MainClass.token1, timeOut = MainClass.to1)
                    time.sleep(8)
                    break
                elif response == 'Unrecognized':
                    MainClass.send_message(f"Your answer is not recognized({k+1}). Write again. y/n", MainClass.token1, timeOut = MainClass.to1)
                    continue
                elif response == 'TiU':
                    # stopScript(pid)
                    MainClass.send_message("Response timed out. LS Tracker continues to work", MainClass.token1, timeOut = MainClass.to1)
                    # for j in range(3):
                    #     response = wait_for_user_response(timeout = 1800)
                    #     if response == "YES":
                    #         resumeScript(pid)
                    #         MainClass.send_message("The script was continued", MainClass.token1, timeOut = MainClass.to1)
                    #         break
                    #     elif response == 'NO':
                    #         MainClass.send_message("The script was not continued", MainClass.token1, timeOut = MainClass.to1)
                    #         break
                    #     elif response == 'Unrecognized':
                    #         MainClass.send_message(f"Your answer is not recognized({j+1}). Write again. y/n", MainClass.token1, timeOut = MainClass.to1)
                    #     elif response == 'TiU':
                    #         MainClass.send_message("Response timed out. Exit")
                    #         return
                    break
        time.sleep(5)
if __name__ == "__main__":
    main()