from mainClass import MainClass
import subprocess
import time
from time import sleep
import random
from pyautogui import press

MainClass.moveTerminal()
race = input("\t1 - Elf\n\t2 - Orc\n\t3 - Dead\n\t4 - Human\n\t5 - Dwarf\nSelect race: ")
location = input("\t1 - Tree Abode\n\t2 - Xinta Right\n\t3 - Xinta Left\nSelect location: ")
bagSize = input("  Enter your bag size (Default = 35): ")
if bagSize.isdigit():
    bagSize = int(bagSize)
else:
    print("  The bag size is incorrect. Use default")
    bagSize = 35 
ch = MainClass(race, 0)
ch.savePID()
point, timeUntilRestart = "right", 600
routeTree1A = (30, 3), (19, 4), (13, 4)
routeTree1B = (29, 8), (17, 7), (12, 2)
routeXintaRight = (41, 31), (29, 32), (29, 32), (34, 23), (32, 12)
routeXintaRight2 = (32, 12), (34, 23)
routeXintaLeft = (41, 31), (29, 32), (29, 32), (19, 27), (18, 20), (16, 12)
pointsXL = (21, 10), (21, 11), (21, 12), (20, 10), (20, 11), (20, 12)
ch.relogin()
farmStartTime = time.time()
process = subprocess.Popen(['python3', 'walkClanMessages.py'])
ch.activate()
if ch.checkInTheCity():
    if location == "1":
        if ch.defineTheCityImage('TreeAbode'):
            def checkBagAndGo(notCheck = False):
                if notCheck:
                    ch.emptyBackpack(bagSize = bagSize)
                else:
                    bgfull = ch.bagFullness(bagSize = bagSize)
                    if bgfull == 'FULL':
                        ch.outOfCharacter()
                        ch.emptyBackpack(bagSize = bagSize)
                    elif bgfull == 'NOTFULL' or  bgfull == 'FALSE':
                        ch.outOfCharacter()
                ch.leaveTheCity()
                ch.startMove()
                randRoute = random.randint(1, 2)
                if randRoute == 1:
                    ch.followTheRoutePumpkin(routeTree1A, unit = "Camel", collect=False)
                elif randRoute == 2:
                    ch.followTheRoutePumpkin(routeTree1B, unit = "Camel", collect=False, exactCoors=(17, 7))
            checkBagAndGo()
            lap, side, fails = 0, "1", 0
            while True:
                if lap > 0 and lap % 7 == 0:
                    if not bagChecked:
                        bgfull = ch.bagFullness(bagSize = bagSize)
                        if bgfull == 'FULL':
                            bagChecked = False
                            process.terminate()
                            ch.relogin()
                            farmStartTime = time.time()
                            process = subprocess.Popen(['python3', 'walkClanMessages.py'])
                            ch.activate()
                            if ch.checkInTheCity():
                                if ch.defineTheCityImage('TreeAbode'):
                                    checkBagAndGo(notCheck = True)
                                else:
                                    process.terminate()
                                    print("ANOTHER CITY")
                                    fails += 1
                            else:
                                process.terminate()
                                print("NOT IN CITY")
                                fails += 1
                        elif bgfull == 'NOTFULL':
                            ch.outOfCharacterMap()
                            bagChecked = False
                        elif bgfull == 'FALSE':
                            ch.outOfCharacterMap()
                farmGold = ch.farmingGold(magic = False, magnetAngle = side) 
                if farmGold == "Battle":
                    lap += 1
                    fails = 0
                    bagChecked = False
                elif farmGold == "KILLED":
                    fails = 0
                elif farmGold == "FAILED":
                    fails += 1 
                elif farmGold == "NOBOTS":
                    fails += 1
                    sleep(1)
                    if ch.noNPC > 0 and ch.noNPC % 3 == 0:
                        press('left', presses = 18)
                elif farmGold == "FailedBattle":
                    fails += 1 
                    lap += 1
                    bagChecked = False
                if lap > 0 and lap % 6 == 0:
                    sleep(.5)
                    press('right', presses = 20)
                    farmGold = ch.farmingGold(magic = False, magnetAngle = side)
                    ch.toCenter()
                    for _ in range(3):
                        if ch.moveOnMap(14 +  random.randint(-1, 1), 10, npcAttack = False, iters = 1):
                            break
                    press('left', presses = 20)
                    sleep(.5)
                if time.time() > farmStartTime + timeUntilRestart:
                    ch.send_message("More than 10 minutes without restart", ch.token2)
                    process.terminate()
                    ch.relogin()
                    farmStartTime = time.time()
                    process = subprocess.Popen(['python3', 'walkClanMessages.py'])
                    ch.activate()
                    if ch.checkInTheCity():
                        if ch.defineTheCityImage('TreeAbode'):
                            checkBagAndGo()
                            bagChecked = False
                if fails >= 10:
                    ch.send_message("MORE 10 FAILS | sleep 60 sec", ch.token2, timeOut = ch.to1)
                    sleep(60)
                    process.terminate()
                    ch.relogin()
                    farmStartTime = time.time()
                    process = subprocess.Popen(['python3', 'walkClanMessages.py'])
                    ch.activate()
                    if ch.checkInTheCity():
                        if ch.defineTheCityImage('TreeAbode'):
                            checkBagAndGo()
                            bagChecked = False
                if ch.noNPC >= 100:
                    print("NPCs are missing. More 100 Attempts")
                    break
                sleep(.2)
        else:
            process.terminate()
            print("ANOTHER CITY")
    elif location == "2" or  location == "3":
        if ch.defineTheCityImage('Xinta'):
            def checkBagAndGo(notCheck = False):
                if notCheck:
                    ch.emptyBackpack(bagSize = bagSize)
                else:
                    bgfull = ch.bagFullness(bagSize = bagSize)
                    if bgfull == 'FULL':
                        ch.outOfCharacter()
                        ch.emptyBackpack(bagSize = bagSize)
                    elif bgfull == 'NOTFULL' or  bgfull == 'FALSE':
                        ch.outOfCharacter()
                ch.leaveTheCity()
                ch.startMove()
                if location == '2':
                    ch.followTheRoutePumpkin(routeXintaRight, unit = "Camel", collect=True)
                else:
                    ch.followTheRoutePumpkin(routeXintaLeft, unit = "Camel", collect=True, exactCoors=(18, 20))
            checkBagAndGo()
            lap, side, fails = 0, "1", 0
            while True:
                if lap > 0 and lap % 7 == 0:
                    if not bagChecked:
                        bgfull = ch.bagFullness(bagSize = bagSize)
                        if bgfull == 'FULL':
                            bagChecked = False
                            process.terminate()
                            ch.relogin()
                            farmStartTime = time.time()
                            process = subprocess.Popen(['python3', 'walkClanMessages.py'])
                            ch.activate()
                            if ch.checkInTheCity():
                                if ch.defineTheCityImage('Xinta'):
                                    checkBagAndGo(notCheck = True)
                                else:
                                    process.terminate()
                                    print("ANOTHER CITY")
                                    fails += 1
                            else:
                                process.terminate()
                                print("NOT IN CITY")
                                fails += 1
                        elif bgfull == 'NOTFULL':
                            ch.outOfCharacterMap()
                            bagChecked = False
                        elif bgfull == 'FALSE':
                            ch.outOfCharacterMap()
                farmGold = ch.farmingGold(magic = False, magnetAngle = side) 
                if farmGold == "Battle":
                    lap += 1
                    fails = 0
                    bagChecked = False
                elif farmGold == "KILLED":
                    fails = 0
                elif farmGold == "FAILED":
                    fails += 1 
                elif farmGold == "NOBOTS":
                    fails += 1
                    sleep(1)
                elif farmGold == "FailedBattle":
                    fails += 1 
                    lap += 1
                    bagChecked = False
                if lap > 0 and lap % 8 == 0:
                    if location == '2':
                        ch.followTheRoutePumpkin(routeXintaRight2)
                        ch.farmingGold(magic=False)
                        ch.moveOnMap(26, 32, npcAttack = False)
                        ch.farmingGold(magic=False)
                        ch.moveOnMap(26, 32, npcAttack = False)
                        ch.followTheRoutePumpkin(list(reversed(routeXintaRight2)))
                    else:
                        curPoint = random.choice(pointsXL)
                        ch.moveOnMap(curPoint[0], curPoint[1], npcAttack = False)
                if time.time() > farmStartTime + timeUntilRestart:
                    ch.send_message("More than 10 minutes without restart", ch.token2)
                    process.terminate()
                    ch.relogin()
                    farmStartTime = time.time()
                    process = subprocess.Popen(['python3', 'walkClanMessages.py'])
                    ch.activate()
                    if ch.checkInTheCity():
                        if ch.defineTheCityImage('Xinta'):
                            checkBagAndGo()
                            bagChecked = False
                if fails >= 10:
                    ch.send_message("MORE 10 FAILS | sleep 60 sec", ch.token2, timeOut = ch.to1)
                    sleep(60)
                    process.terminate()
                    ch.relogin()
                    farmStartTime = time.time()
                    process = subprocess.Popen(['python3', 'walkClanMessages.py'])
                    ch.activate()
                    if ch.checkInTheCity():
                        if ch.defineTheCityImage('Xinta'):
                            checkBagAndGo()
                            bagChecked = False
                if ch.noNPC >= 100:
                    print("NPCs are missing. More 100 Attempts")
                    break
                sleep(.2)
        else:
            process.terminate()
            print("ANOTHER CITY")
else:
    process.terminate()
    print("NOT IN CITY")
ch.send_message("Farm Silk FINISH", ch.token1, timeOut = ch.to1)
process.terminate()

try:
    subprocess.run(f'wmctrl -a "{MainClass.username}@"', shell=True, check=True)
    sleep(3)
except Exception as ex:
    print(ex)