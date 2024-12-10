from mainClass import MainClass
import subprocess
from time import sleep
import random
from ahk import AHK

MainClass.moveTerminal()
race = input("\t1 - Elf\n\t2 - Orc\n\t3 - Dead\n\t4 - Human\n\t5 - Dwarf\nSelect race: ")
location = input("\t  1 - Bats\n\t  2 - Pumpkins\nSelect location: ")
ch = MainClass(race, 0)
ch.savePID()
routes = {
    "routeAoFLeft": (
        (14, 45, (0, 0, 1200, 1200)),
        (3, 34, (0, 0, 600, 600)),
        (3, 25, "noFarm"),
        (1, 19, (0, 0, 600, 700)),
        (4, 11, "noFarm"),
        (11, 5, (0, 0, 800, 450)),
        (22, 7, (200, 0, 600, 750)),
        (28, 4, (200, 0, 600, 500)), 
        (38, 8, (75, 0, 800, 700)),
        (43, 8, (0, 0, 900, 700)),
        (47, 13, (500, 0, 500, 700)),
        (45, 20, (0, 0, 1200, 1200)),
        (47, 25, (0, 0, 1200, 1200)),
        (46, 30, (500, 100, 500, 700)),
        (46, 42, (350, 350, 650, 650)),
        (33, 43, (100, 200, 650, 600)),
        (27, 34, "noFarm"),
	(25, 28, "noFarm"),
        (26, 22, (200, 0, 700, 500)),
        (17, 21, (100, 50, 550, 550)),
        (18, 26, "noFarm"),
        (17, 35, "noFarm")),
    "routeAoFCloud": ((23, 45), (35, 48), (47, 47), (47, 36)),
    "routePumpkin1": ((6, 22), (14, 15), (22, 13), (22, 22), (28, 17), (33, 13), (40, 17), (38, 26), (43, 31), (33, 33), (33, 39), (26, 43), (24, 36), (18, 35), (14, 39), (11, 33), (7, 27))
}
routes["routeAoFRight"] = list(reversed(routes["routeAoFLeft"]))
routes["routePumpkin2"] = list(reversed(routes["routePumpkin1"]))
zero, bats = False, True
currentRoute = random.choice(("routeAoFLeft", "routeAoFRight"))
if location == "2":
    currentRoute, zero, bats = random.choice(("routePumpkin1", "routePumpkin2")), True, False
lap, side, fails = 0, "2", 0

ch.relogin()
process = subprocess.Popen(['py', 'walkClanMessages.py'])
ch.activate()
if ch.checkInTheCity():
    if ch.defineTheCityImage('AbodeOfFear'):
        ch.leaveTheCity()
        ch.startMove(firstKey='left')
        if location == "2":
            ch.followTheRoutePumpkin(routes["routeAoFCloud"])
            ch.crossToNextMap(49, 29)
            ch.startMove()
        while True:
            if location == "1":
                ftr = ch.followTheRouteBats(routes[currentRoute], collect = True, zero=zero, side = side, bats = bats)
            elif location == "2":
                ftr = ch.followTheRoutePumpkin(routes[currentRoute], collect = True, zero=zero, side = side, bats = bats)
            if ftr:
                fails, lap = 0, lap + 1
                ch.send_message(f"LAP {lap}", token=ch.token2)
            else:
                fails, lap = fails + 1, lap + 1
                process.terminate()
                ch.relogin()
                process = subprocess.Popen(['py', 'walkClanMessages.py'])
                ch.activate()
                if ch.checkInTheCity():
                    if ch.defineTheCityImage('AbodeOfFear'):
                        ch.leaveTheCity()
                        ch.startMove(firstKey='left')
                        if location == "2":
                            ch.followTheRoutePumpkin(routes["routeAoFCloud"])
                            ch.crossToNextMap(49, 29)
                            ch.startMove(firstKey='left')
                    else:
                        process.terminate()
                        print("ANOTHER CITY")
                        fails += 1
                else:
                    process.terminate()
                    print("NOT IN CITY")
                    fails += 1
            if fails >= 3:
                print("More 3 Fails in the row. Break")
                break
            if lap > 0 and lap % 50 == 0:
                ch.send_message("Change the route and side", ch.token2)
                if currentRoute == "routeAoFLeft":
                    currentRoute = "routeAoFRight"
                elif currentRoute == "routeAoFRight":
                    currentRoute = "routeAoFLeft"
                elif currentRoute == "routePumpkin1":
                    currentRoute = "routePumpkin2"
                elif currentRoute == "routePumpkin2":
                    currentRoute = "routePumpkin1"
                if side == '2':
                    side = '3'
                elif side == '3':
                    side = '2' 
            if ch.noNPC >= 100:
                print("NPCs are missing. More 100 Attempts")
                break
    else:
        process.terminate()
        print("ANOTHER CITY")
else:
    process.terminate()
    print("NOT IN CITY")

ch.send_message("Farm Pumpkin FINISH", ch.token1, timeOut = ch.to1)

try:
    ahk = AHK()
    win = ahk.find_window(title = 'Windows PowerShell')
    if win:
        win.activate()
except Exception as ex:
	print(ex)
