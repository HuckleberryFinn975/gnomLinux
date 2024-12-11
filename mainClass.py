import requests
import subprocess, os
import pyautogui
import random
from pyautogui import click, press
import time
import math
import json
from time import sleep
from recognize import recognize
from recognizeLetters import recognizeLetters
from cities import cityTranslate
pyautogui.FAILSAFE = False

jsonPath = "/oaData/tgData.json"
with open(jsonPath, 'r') as file:
    tgData = json.load(file)

log_file_path = "logOasis.txt"
data = {"titles": {"1": "ELF","2": "ORC", "3": "DEAD", "4": "HUMAN", "5": "DWARF"},
		"images": {"1": "Elf", "2": "Orc", "3": "Dead", "4": "Human", "5": "Dwarf"}}
equipmentCoors = {"helmet": 195, "amulet": (255, 420), "weapon": (470, 530), "armour": 585, "boots": 630, "flag": 690}

class MainClass:
	farm12, battleNumber, noNPC, npcCount = 1, 0, 0, 1
	joinedBots, startUnit = 0, "Griffin"
	lastBot, endingIndex, botListLenght = (0,0), 0, 0
	dissed = False
	startX, startY = 17, 170
	token1, token2, to1, username = tgData["pushToken"], tgData["followToken"], 5, tgData["username"]

	def __init__(self, race, flead):
		self.race = race
		self.flead = flead
 
	@classmethod
	def send_message(self, message, token, timeOut = .3, chat_id = tgData["chat_id"]):
		print(message)
		try:
			root_url = 'https://api.telegram.org/bot'
			url = f"{root_url}{token}/sendMessage"
			requests.post(url, json = {'chat_id': chat_id, 'text': message}, timeout = timeOut)
		except Exception as ex:
			print(ex)
	@classmethod
	def savePID(self):
		pid = os.getpid()
		with open("./game.pid", "w") as f:
			f.write(str(pid))
	@classmethod
	def moveTerminal(self):
		try:
			subprocess.run(f'wmctrl -r "{self.username}@" -e 0,1050,0,400,900', shell=True, check=True)
			sleep(3)
		except Exception as ex:
			print(ex)
	def killWindow(self):
		command = f''' wmctrl -c -F -ir $(wmctrl -l | grep "{data['titles'][self.race]}" | cut -d' ' -f1)'''
		try:
			subprocess.run(command, shell=True, check=True)
			self.send_message("Killed OASIS", self.token2)
		except Exception as ex:
			print(ex)
	def setWindow(self):
		print(f"{data['images'][self.race]} | setting Window")
		try:
			subprocess.run(f'''wmctrl -r "{data['titles'][self.race]}" -e 0,0,0,950,1000''', shell=True, check=True)
			sleep(3)
		except Exception as ex:
			print(ex)
	def runWindow(self):
		self.endingIndex = 0
		with open(log_file_path, 'w'):
			pass
		command = f'''java -jar ./Clients/{data["images"][self.race]}.jar &'''
		try:
			self.send_message(f"Running {data['images'][self.race]} | sleep 7...", self.token2)
			with open(log_file_path, "a") as log_file:
				subprocess.run(command, shell = True, stdout=log_file, stderr=subprocess.DEVNULL)
			sleep(7)
		except Exception as ex:
			print(ex)
	def relogin(self):
		self.killWindow()
		sleep(1)
		self.runWindow()
		self.setWindow()
		press('enter')
		sleep(5)
	@classmethod
	def rightSoft(self):
		click(850, 930)
	@classmethod
	def leftSoft(self):
		click(450, 930)
	def activate(self):
		try:
			subprocess.run(f'''wmctrl -a "{data['titles'][self.race]}"''', shell=True, check=True)
		except Exception as ex:
			print(ex)
	@classmethod
	def toCenter(self):
		self.rightSoft()
		centerBut = pyautogui.locateOnScreen(f"img/collection/toCenter.png", minSearchTime=2, region=(500,0,780,1024), confidence=.9)
		if centerBut:
			print("found cetner Button | sleep .5")
			click(centerBut)
			sleep(.5)
		else:
			print("do not SEE CENTER BOTTON")
	def logHandler(self, keyPhrase, stop = False):
		print(f"\t\tRead log file | Start with {self.endingIndex}")
		with open(log_file_path, 'r') as file:
			file = file.read()
		if stop:
			position = file.rfind(keyPhrase, self.endingIndex, self.endingIndex + 30)
		else:
			position = file.rfind(keyPhrase, self.endingIndex)
		if position != -1:
			self.endingIndex = position + len(keyPhrase)
			print(f'\t\tLOG SUCCES "{keyPhrase}" found on position {position}')
			return True
		else:
			print(f'\t\t!!! LOG FAILED "{keyPhrase}" not found within range [{self.endingIndex} - end]')
			return False
	def logLeadershipHandler(self, fullLead, keyPhrase = "text = Лидерство:"):
		print(f"LS the log file | Start with {self.endingIndex}")
		with open(log_file_path, 'r') as file:
			file = file.read()
		position = file.rfind(keyPhrase, self.endingIndex)
		if position != -1:
			print(f'  LOG 1 SUCCES {keyPhrase} found on position {position}')
			leadPosition = file.find("7+", position)
			if leadPosition:
				print(f'    LOG 2 SUCCES "7+" found on position {leadPosition}')
				lead = file[leadPosition + 2 : leadPosition + 6]
				print(f"    Skill is {lead}")
				if lead == fullLead:
					print(f"      Skill is full | Log check is successful")
					return True
				else:
					print(f"      Skill is not full - {lead}")
					return False
			else:
				print(f"    Can't find '7+'")
				return False
		else:
			print(f'  log FAILED {keyPhrase} not found within range [{self.endingIndex} - end]')
			return False
	def logWalkHandler(self, keyPhrase = "client -> server: 61 wait for: 0"):
		print(f"\t\tRead log file | Start with {self.endingIndex}")
		with open(log_file_path, 'r') as file:
			file = file.read()
		position = file.rfind(keyPhrase)
		if position != -1:
			print(f'\t\tLOG SUCCES "{keyPhrase}" found on position {position}')
			heroCoors = file[position - 7:position].replace(')', '').replace('(', '').replace('t', '').replace('c', '').split()
			print(f"  {heroCoors}")
			self.endingIndex = position + len(keyPhrase)
			return (heroCoors[0], heroCoors[1])
		else:
			print(f'\t\tlog FAILED "{keyPhrase}" not found within range [{self.endingIndex} - end]')
			return False
	def clMessageCheck(self, keyPhrase = "server -> client: 18"):
		print(f"Check CLAN MESSAGES | Start with {self.endingIndex}")
		with open(log_file_path, 'r') as file:
			file = file.read()
		position = file.find(keyPhrase, self.endingIndex)
		if position != -1:
			self.endingIndex = position + len(keyPhrase)
			print("  A clan message appeared")
			self.leftSoft()
			return True
		else:
			print("  NO CLAN MESSAGES")
			return False
	def clMessageCheckImage(self):
		print("\t\tClan Messages Image Check")
		clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=2, region=(0,500,1280, 524), confidence=.85)
		if clanMessage:
			print("\t\tSee clan message IMAGE")
			self.leftSoft()
			return True
		else:
			print("\t\tDon't see clan message IMAGE")
			return False
	def checkInTheCity(self):
		print("Search inTheCity")
		for _ in range(6):
			inTheCity = pyautogui.locateOnScreen(f"img/collection/inTheCity.png", minSearchTime=4, region=(0,0,1280, 1024), confidence=.8)
			if inTheCity:
				self.send_message("  The character is in the city", self.token2)
				return True
			print("  Don't see inTheCity")
			if self.clMessageCheckImage():
				continue
		self.send_message("    NO SEE IN THE CITYs | FALSE", self.token2)
		return False
	def defineTheCity(self):
		self.send_message("Recognize the name of the city", self.token2)
		for _ in range(3):
			cityX, cityY = 510, 50
			pyautogui.screenshot(region=(cityX, cityY, 250, 20)).save("cityName.png")
			sleep(.5)
			text = recognizeLetters("cityName.png")
			print(f"  Recognized city is {text} ")
			cityName = cityTranslate.get(text)
			if cityName:
				self.send_message(f"    Hero are in {cityName}", self.token2)
				return cityName
			if self.clMessageCheckImage():
				continue
		self.send_message("    The city is not defined | FALSE", self.token2)
		return False
	def defineTheCityImage(self, neededCity):
		self.send_message("Recognize the name of the city by Image", self.token2)
		for _ in range(3):
			recogCity = pyautogui.locateOnScreen(f"img/collection/city{neededCity}.png", minSearchTime=2, confidence=.9, region=(200, 0, 600, 250))
			if recogCity:
				self.send_message(f"  Succes | Hero are in {neededCity}", self.token2)
				return True
			else:
				print(f"  Don't see {neededCity}")
			if self.clMessageCheckImage():
				continue
		self.send_message(f"     city {neededCity} is not defined | FALSE", self.token2)
		return False
	def openCharacter(self):
		print("Open the character")
		for _ in range(3):
			self.leftSoft()
			hero = pyautogui.locateOnScreen(f"img/collection/hero.png", minSearchTime=2, region=(0,0,780,1024), confidence=.93)
			if hero:
				print("  See heroButton | Click")
				click(hero)
			else:
				print("  Don't see heroButton")
			sleep(.5)
			if self.logHandler("ViewHeroOrHelp()"):
				return True
			characterMenu = pyautogui.locateOnScreen(f"img/collection/characterMenu.png", minSearchTime=2, region=(0,0,680,1024), confidence=.85)
			if characterMenu:
				print("  See the character menu")
				return True
			else:
				print("  Don't see character menu")
			if self.clMessageCheckImage():
				continue
		print("    Characters open Failed | FALSE")
		return False
	def outOfCharacter(self):
		print("Get out of the character")
		for _ in range(3):
			self.rightSoft()
			exit = pyautogui.locateOnScreen(f"img/collection/exit.png", minSearchTime=2, region=(500,0,780,1024), confidence=.93)
			if exit:
				print("  See exit | Click")
				click(exit)
			else:
				print("  Don't see exit")
			print("  Search inTheCity")
			inTheCity = pyautogui.locateOnScreen(f"img/collection/inTheCity.png", minSearchTime=2, region=(0,0,1280, 1024), confidence=.85)
			if inTheCity:
				print("    The character is in the city")
				return True
			else:
				print("    Don't see in the city")
			if self.clMessageCheckImage():
				continue
		print("    NO SEE IN THE CITYs  | FALSE")
		return False
	def outOfCharacterMap(self):
		print("Get out of the character")
		for _ in range(3):
			self.rightSoft()
			exit = pyautogui.locateOnScreen(f"img/collection/exit.png", minSearchTime=2, region=(500,0,780,1024), confidence=.93)
			if exit:
				print("  See exit | Click")
				click(exit)
				sleep(.5)
			else:
				print("  Don't see exit")
			if self.logHandler("SoundPlayer.playMusic() musicID=1"):
				return True
			if self.clMessageCheckImage():
				continue
	def dressingUpSingle(self, coordinate, itemName):
		def undress():
			print("Undress Sinle")
			for _ in range(3):
				pyautogui.doubleClick(1235, equipmentCoors[coordinate])
				sleep(.5)
				if self.logHandler("client -> server: 227 wait for: 227"):
					print("  Item undressed successfully")
					return True
				if self.clMessageCheckImage():
					continue
			self.send_message("  Undressing FAILED", self.token2)
			return False
		def extraCheck():
			print("Extra item check")
			subjects = pyautogui.locateAllOnScreen(f"img/collection/item{itemName}.png", region=(0,0,480,1024), confidence=.95)
			if subjects:
				listSubjects = list(subjects)
				print(f"  See {len(listSubjects)} {itemName}")
				print("  ", listSubjects[0], listSubjects[1])
				click(listSubjects[1])
				subjectExtra = pyautogui.locateOnScreen(f"img/collection/item{itemName}Extra.png", minSearchTime=2, region=(0,0,480,1024), confidence=.95)
				if subjectExtra:
					print(f"    See {itemName}")
					click(listSubjects[1])
					sleep(.5)
					if self.logHandler("client -> server: 230 wait for: 230"):
						self.send_message(f"      {itemName} is dressed", self.token2)
						return True
				else:
					click(listSubjects[0])
					subjectExtra = pyautogui.locateOnScreen(f"img/collection/item{itemName}Extra.png", minSearchTime=2, region=(0,0,480,1024), confidence=.95)
					if subjectExtra:
						print(f"    See {itemName}")
						click(listSubjects[0])
						sleep(.5)
						if self.logHandler("client -> server: 230 wait for: 230"):
							self.send_message(f"      {itemName} is dressed", self.token2)
							return True
			else:
				print(f"  Don't see {itemName}")
		def dress():
			print("Dress Single")
			for _ in range(3):
				click(1235, equipmentCoors[coordinate])
				sleep(.15)
				equipmentSelection = pyautogui.locateOnScreen(f"img/collection/equipmentSelection.png", minSearchTime=2, region=(0,0,680,1024), confidence=.85)
				if equipmentSelection:
					print("  See the equipment selection")
					if itemName not in "AdamantBoots GhostHelmet".split():
						subject = pyautogui.locateOnScreen(f"img/collection/item{itemName}.png", minSearchTime=2, region=(0,0,480,1024), confidence=.95)
						if subject:
							print(f"    See {itemName}")
							pyautogui.doubleClick(subject)
							sleep(.5)
							if self.logHandler("client -> server: 230 wait for: 230"):
								print(f"      Log Right | {itemName} is dressed")
								return True
						else:
							print(f"    Don't see {itemName}")
							self.rightSoft()
					else:
						if extraCheck():
							return True
				else:
					print("  Don't see the equipment selection")
				if self.clMessageCheckImage():
					continue
		undress()
		if dress():
			return True
	def dressingUpMulti(self, coordinate, itemName, prs, type):
		def undress():
			for _ in range(3):
				pyautogui.doubleClick(1235, equipmentCoors[coordinate][0])
				sleep(.5)
				if self.logHandler("client -> server: 227 wait for: 227"):
					print("  Item undressed successfully")
					return True
				if self.clMessageCheckImage():
					continue
			self.send_message("  Undressing FAILED | FALSE", self.token2)
			return False
		def undressing():
			print("Undress Multi")
			for _ in range(prs):
				undress()
			return True
		def dress():
			for _ in range(3):
				click(1235, equipmentCoors[coordinate][1])
				sleep(.15)
				equipmentSelection = pyautogui.locateOnScreen(f"img/collection/equipmentSelection.png", minSearchTime=2, region=(0,0,680,1024), confidence=.85)
				if equipmentSelection:
					print("  See the equipment selection")
					subject = pyautogui.locateOnScreen(f"img/collection/item{itemName}.png", minSearchTime=2, region=(0,0,480,1024), confidence=.95)
					if subject:
						print(f"    See {itemName}")
						pyautogui.doubleClick(subject)
						sleep(.5)
						if self.logHandler("client -> server: 230 wait for: 230"):
							self.send_message(f"      Log Right | {itemName} is dressed", self.token2)
							return True
					else:
						print(f"    Don't see {itemName}")
						self.rightSoft()
				else:
					print("  Don't see the equipment selection")
				if self.clMessageCheckImage():
					continue
		def dressing():
			print("Dressing Multi")
			click(1235, equipmentCoors[coordinate][1])
			for _ in range(prs):
				dress()
		undressing()
		dressing()
	def checkLeadership(self):
		print("Check full Leadership")
		for _ in range(3):
			if self.logLeadershipHandler("1238"):
				print("  The leadership is full | get out character")
				if self.outOfCharacter():
					print("    exit from the character Successful")
					return True
			else:
				print("  Don't see fullLeadership")
			if self.clMessageCheckImage():
				continue
		print("    checkLeadership Failed | FALSE")
		return False
	def dressingUpForLeadership(self, flead = "1238"):
		print("Dressing Up For Leadership")
		sleep(.5)
		if self.logLeadershipHandler(flead):
			self.send_message("  The leadership is full. No need to change clothes", self.token2)
			return True
		else:
			self.dressingUpSingle("boots", "BoneDragonBoots")
		if self.logLeadershipHandler(flead):
			print("  The leadership is full. No need to continue")
			return True
		else:
			self.dressingUpSingle("helmet", "DungeonKeeperHelmet")
		if self.logLeadershipHandler(flead):
			print("  The leadership is full. No need to continue")
			return True
		else:
			self.dressingUpSingle("armour", "BoneDragonCuirass")
		if self.logLeadershipHandler(flead):
			print("  The leadership is full. No need to continue")
			return True
		else:
			self.dressingUpSingle("flag", "GoldenMountainFlag")
		if self.logLeadershipHandler(flead):
			print("  The leadership is full. No need to continue")
			return True
		else:
			self.dressingUpMulti("weapon", "LeadersAx", 2, "Weapon")
		if self.logLeadershipHandler(flead):
			print("  The leadership is full. No need to continue")
			return True
		else:
			self.dressingUpMulti("amulet", "PoisonousTear", 4, "Amulet")
	def dressingUpForBattle(self, fullDeff = "1519"):
		sleep(.5)
		print("Dressing Up For Leadership")
		if self.logLeadershipHandler(fullDeff, keyPhrase = "text = Защита:"):
			print("  The Deffence is full. No need to change clothes")
			return True
		else:
			self.dressingUpSingle("boots", "AdamantBoots")
		if self.logLeadershipHandler(fullDeff, keyPhrase = "text = Защита:"):
			print("  The Deffence is full. No need to change clothes")
			return True

		else:
			self.dressingUpSingle("helmet", "GhostHelmet")
		if self.logLeadershipHandler(fullDeff, keyPhrase = "text = Защита:"):
			print("  The Deffence is full. No need to change clothes")
			return True
		else:
			self.dressingUpSingle("armour", "CharmedMithrilArmor")
		if self.logLeadershipHandler(fullDeff, keyPhrase = "text = Защита:"):
			print("  The Deffence is full. No need to change clothes")
			return True
		else:
			self.dressingUpSingle("flag", "RidgeFlag")
		if self.logLeadershipHandler(fullDeff, keyPhrase = "text = Защита:"):
			print("  The Deffence is full. No need to change clothes")
			return True
		else:
			self.dressingUpMulti("weapon", "MaceOfDeath", 2, "Weapon")
		if self.logLeadershipHandler(fullDeff, keyPhrase = "text = Защита:"):
			print("  The Deffence is full. No need to change clothes")
			return True
		else:
			self.dressingUpMulti("amulet", "SAFE", 4, "Amulet")
	def moveToFirstSlot(self):
		print("Move To First Slot")
		iterNum = 0
		for k in range(4):
			self.leftSoft()
			buttonArmy = pyautogui.locateOnScreen(f"img/collection/buttonArmy.png", minSearchTime=2, region=(0,0,780,1024), confidence=.94)
			if buttonArmy:
				print("  See buttonArmy | Click")
				click(buttonArmy)
			else:
				print("  Don't see buttonArmy")
			equipmentSelection = pyautogui.locateOnScreen(f"img/collection/equipmentSelection.png", minSearchTime=2, region=(0,0,680,1024), confidence=.85)
			if equipmentSelection:
				print("    See the equipment selection | Click 1st squad ")
				click(45, 195)
				plusMinus = pyautogui.locateOnScreen(f"img/collection/plusMinus.png", minSearchTime=2, region=(700,0,580,1024), confidence=.92)
				if plusMinus:
					print("      See plusMinus | Click ")
					click(plusMinus)
					press('enter')
					sleep(1)
				self.logHandler("client -> server: 147 wait for: 20")
				click(45, 195)
				combine = pyautogui.locateOnScreen(f"img/collection/combine.png", minSearchTime=2, region=(0,0,780,1024), confidence=.92)
				if combine:
					print("      See Combine | Click ")
					click(combine)
					sleep(1)
					if self.logHandler("client -> server: 148 wait for: 20"):
						print("        Combine Log right | Moving to 1 slot Successful")
						click(45, 195)
						return True
					click(45, 195)
					plusMinus = pyautogui.locateOnScreen(f"img/collection/plusMinus.png", minSearchTime=2, region=(700,0,580,1024), confidence=.92)
					if plusMinus:
						print("        See plusMinus | Moving to 1 slot Successful")
						return True
				else:
					print("      Don't see combine ")
					equipmentSelection = pyautogui.locateOnScreen(f"img/collection/equipmentSelection.png", minSearchTime=2, region=(0,0,680,1024), confidence=.85)
					if equipmentSelection:
						if iterNum > 1:
							print("      iterations > 1. emptyCheck")
							emptySquad = pyautogui.locateOnScreen(f"img/collection/emptySquad.png", minSearchTime=2, region=(0,0,300,300), confidence=.92)
							if emptySquad:
								print("        See Empty squad | Moving to 1 slot Successful")
								return True
						print("      See the equipment selection | Continue")
						iterNum += 1
						print("      iterations +1")
						continue
			if self.clMessageCheckImage():
				continue
			iterNum += 1
			print("  iterations +1")
			if k == 2:
				self.outOfCharacterMap()
			print("  4 iterations. possible problems. Move to 1 slot complete")
		return True
	def leaveOneSquad(self):
		print("Leave 1 squad")
		for _ in range(5):
			self.leftSoft()
			buttonArmy = pyautogui.locateOnScreen(f"img/collection/buttonArmy.png", minSearchTime=2, region=(0,0,780,1024), confidence=.94)
			if buttonArmy:
				print("  See buttonArmy | Click")
				click(buttonArmy)
			else:
				print("  Don't see buttonArmy")
			equipmentSelection = pyautogui.locateOnScreen(f"img/collection/equipmentSelection.png", minSearchTime=2, region=(0,0,680,1024), confidence=.85)
			if equipmentSelection:
				print("  See the equipment selection | Click 1st squad | disband")
				for _ in range(6):
					click(45, 195)
					self.rightSoft()
					disband = pyautogui.locateOnScreen(f"img/collection/disband.png", minSearchTime=2, region=(500,0,780,1024), confidence=.92)
					if disband:
						print("    See disband | Click ")
						click(disband)
						press('enter', presses=2)
				self.rightSoft()
				exit = pyautogui.locateOnScreen(f"img/collection/exit.png", minSearchTime=2, region=(500,0,780,1024), confidence=.93)
				if exit:
					print("  See exit | Click")
					click(exit)
				else:
					print("  Don't see exit")
				print("  Search inTheCity")
				inTheCity = pyautogui.locateOnScreen(f"img/collection/inTheCity.png", minSearchTime=2, region=(0,0,1280, 1024), confidence=.85)
				if inTheCity:
					print("    The character is in the city | SUCCES")
					return True
				else:
					print("    Don't see inTheCity")
			if self.clMessageCheckImage():
				continue
		print("  Leaving one squad failed  | FALSE")
		return False
	def leaveOneUnit(self):
		print("Trying to leave one unit")
		def splitDissband():
			print("Split and disband | Only 1 unit leave")
			for _ in range(3):
				plusMinus = pyautogui.locateOnScreen(f"img/collection/plusMinus.png", minSearchTime=2, region=(700,0,580,1024), confidence=.92)
				if plusMinus:
					print("  See plusMinus | Click")
					click(plusMinus)
					press('enter')
					sleep(1)
				click(45, 195)
				self.logHandler("client -> server: 147 wait for: 20")
				combine = pyautogui.locateOnScreen(f"img/collection/combine.png", minSearchTime=2, region=(0,0,780,1024), confidence=.92)
				if combine:
					print("  See Combine ")
					self.rightSoft()
					disband = pyautogui.locateOnScreen(f"img/collection/disband.png", minSearchTime=2, region=(500,0,780,1024), confidence=.92)
					if disband:
						print("    See disband | Click ")
						click(disband)
						press('enter', presses=2)
						if self.logHandler("client -> server: 144 wait for: 0"):
							print("      Right LOG | Disband of the large squad Successful. 1 unit  left")
							return True
						equipmentSelection = pyautogui.locateOnScreen(f"img/collection/equipmentSelection.png", minSearchTime=2, region=(0,0,680,1024), confidence=.85)
						if equipmentSelection:
							print("      See the equipment selection ")
							emptySquad = pyautogui.locateOnScreen(f"img/collection/emptySquad.png", minSearchTime=2, region=(0,0,300,300), confidence=.92)
							if emptySquad:
								print("        See Empty squad | Disband of the large squad Successful. 1 unit  left")
								return True
							continue
				if self.clMessageCheckImage():
					continue
		if self.moveToFirstSlot():
			splitDissband()
			if self.outOfCharacter():
				return True
	def bastion(self):
		print("Trying to open the Bastion")
		for _ in range(3):
			bastion = pyautogui.locateOnScreen(f"img/collection/townBastion.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
			if bastion:
				print("  See Bastion | Click | Search barrack")
				click(bastion)
			if self.logHandler("client -> server: 72 wait for: 74"):
				print("  Right LOG | Bastion Succes")
				return True
			barrack = pyautogui.locateOnScreen(f"img/collection/townBarrack.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
			if barrack:
				print("  See Barrack | Bastion Succes")
				return True
			if self.clMessageCheckImage():
				continue
		print("Can't open Bastion | FALSE")
		return False
	def seeArmy(self):
		print("Trying to see the Army")
		def openArmy():
			print("Trying to open the yoyr Army")
			for _ in range(3):
				yourArmy = pyautogui.locateOnScreen(f"img/collection/townYourArmy.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
				if yourArmy:
					print("  See yourArmy | Click | Search inside yourArmy")
					click(yourArmy)
				if self.logHandler("client -> server: 216 wait for: 153"):
					print("  Right LOG | OpenArmy Succes")
					return True
				equipmentSelection = pyautogui.locateOnScreen(f"img/collection/equipmentSelection.png", minSearchTime=2, region=(0,0,680,1024), confidence=.85)
				if equipmentSelection:
					print("  See the equipment selection | OpenArmy Succes")
					return True
				if self.clMessageCheckImage():
					continue
			print("    Can't open yourArmy | FALSE")
			return False
		if self.bastion():
			if openArmy():
				return True
	def openInn(self):
		print("Run openInn method")
		def openInn():
			print("Trying to open the Inn")
			for _ in range(3):
				yourInn = pyautogui.locateOnScreen(f"img/collection/townInn.png", minSearchTime=2, region=(0,0,1280,524), confidence=.93)
				if yourInn:
					print("  See yourInn | Click | Search inside yourInn")
					click(yourInn)
				if self.logHandler("client -> server: 216 wait for: 153"):
					print("  Right LOG | townInn Succes")
					return True
				insideBarracks = pyautogui.locateOnScreen(f"img/collection/insideBarracks.png", minSearchTime = 2, region = (600,0,680,524), confidence=.9)
				if insideBarracks:
					print("  See insideBarracks | TownInn Succes")
					return True
				if self.clMessageCheckImage():
					continue
			print("    Can't open yourInn | FALSE")
			return False
		if self.bastion():
			if openInn():
				return True
	def exitArmy(self):
		print("Exit from Army")
		def getOut():
			print("Get out of the Army")
			for _ in range(3):
				self.rightSoft()
				exit = pyautogui.locateOnScreen(f"img/collection/exit.png", minSearchTime=2, region=(500,0,780,1024), confidence=.93)
				if exit:
					print("  See exit | Click")
					click(exit)
				else:
					print("  Don't see exit")
				if self.logHandler("SoundPlayer.playMusic() musicID=2"):
					print("  Get out of Army Succes")
					return True
				print("  Search Barrack")
				barrack = pyautogui.locateOnScreen(f"img/collection/townBarrack.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
				if barrack:
					print("    See fromBarracks | Leave Bastion Succes")
					return True
				else:
					print("    Don't see Barrack")
				if self.clMessageCheckImage():
					continue
			print("CAN'T GETOUT ARMY | FALSE")
			return False
		def exit():
			print("Trying to leave Bastion")
			for _ in range(5):
				barrack = pyautogui.locateOnScreen(f"img/collection/townBarrack.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
				if barrack:
					print("  See fromBarracks | Leave Bastion")
					self.rightSoft()
				else:
					print("  Don't see fromBarracks")
				print("  Search inTheCity")
				inTheCity = pyautogui.locateOnScreen(f"img/collection/inTheCity.png", minSearchTime=2, region=(0,0,1280, 1024), confidence=.85)
				if inTheCity:
					print("    The character is in the city")
					return True
				else:
					print("    Don't see inTheCity")
				if self.clMessageCheckImage():
					continue
			print("  Can't Exit from bastion | FALSE")
			return False
		if getOut():
			if exit():
				return True
	def hireAnArmy(self, unit):
		print("Hire an Army")
		def barrack():
			print("Trying to open the barracks")
			for _ in range(3):
				barrack = pyautogui.locateOnScreen(f"img/collection/townBarrack.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
				if barrack:
					print("  See Barrack | Click | Search inside barrack")
					click(barrack)
				if self.logHandler("client -> server: 216 wait for: 153"):
					print("  Right LOG | Barrack Succes")
					return True
				insideBarracks = pyautogui.locateOnScreen(f"img/collection/insideBarracks.png", minSearchTime=2, region=(600,0,680,524), confidence=.9)
				if insideBarracks:
					print("  See insideBarracks | Barrack Succes")
					return True
				if self.clMessageCheckImage():
					continue
			print("    Can't open Barracks | FALSE")
			return False
		def buyUnits(unit):
			def enter(unit):
				print("Trying to buy units")
				for _ in range(5):
					unitImage = pyautogui.locateCenterOnScreen(f"img/collection/barrack{unit}.png", minSearchTime=2, region=(200,0,900,524), confidence=.94)
					if unitImage:
						print(f"  See Unit {unitImage[0]} {unitImage[1]} | Click | Recruit to the max")
						click(unitImage)
						sleep(.2)
						click(unitImage)
						sleep(.5)
						self.rightSoft()
					else:
						print("  Don't see Unit")
					recruitMax = pyautogui.locateOnScreen(f"img/collection/recruitMax.png", minSearchTime=2, region=(500,0,780,1024), confidence=.9)
					if recruitMax:
						print("  See recruitMax | Click | Hiring")
						click(recruitMax)
						sleep(.5)
						self.rightSoft()
					else:
						print("  Don't see recruitMax")
					hire = pyautogui.locateOnScreen(f"img/collection/hire.png", minSearchTime=2, region=(500,0,780,1024), confidence=.9)
					if hire:
						print("  See hire | Click | Hiring")
						click(hire)
						sleep(2.5)
					else:
						print("  Don't see Hire button")
					if self.logHandler("client -> server: 101 wait for: 20"):
						print("  Right LOG | Hiring Succes")
						return True
					barrack = pyautogui.locateOnScreen(f"img/collection/townBarrack.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
					if barrack:
						print("  See fromBarracks | Enter complete")
						return True
					else:
						print("  Don't see fromBarracks")
					if self.clMessageCheckImage():
						continue
				print("    Could not buy an army | FALSE")
				return False
			def exit():
				print("Trying to leave Bastion")
				for _ in range(5):
					barrack = pyautogui.locateOnScreen(f"img/collection/townBarrack.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
					if barrack:
						print("See fromBarracks | Leave Bastion")
						self.rightSoft()
					else:
						print("Don't see fromBarracks")
					print("Search inTheCity")
					inTheCity = pyautogui.locateOnScreen(f"img/collection/inTheCity.png", minSearchTime=2, region=(0,0,1280, 1024), confidence=.85)
					if inTheCity:
						print("The character is in the city")
						return True
					else:
						print("Don't see inTheCity")
					if self.clMessageCheckImage():
						continue
				print("  Can't buy. Exit from bastion | FALSE")
				return False
			if enter(unit):
				if exit():
					return True
		if self.bastion():
			if barrack():
				if buyUnits(unit):
					return True
	def recruitFromInn(self, unit):
		print("Recruit an Army from Inn")
		def buyUnits(unit):
			def enter(unit):
				print("Trying to recruit units")
				for _ in range(5):
					unitImage = pyautogui.locateCenterOnScreen(f"img/collection/barrack{unit}.png", minSearchTime=2, region=(0,225,900,524), confidence=.94)
					if unitImage:
						print(f"  See Unit {unitImage[0]} {unitImage[1]} | Click | Recruit to the max")
						click(unitImage)
						sleep(.2)
						click(unitImage)
						sleep(.5)
						self.rightSoft()
					else:
						print("  Don't see Unit")
					recruitMax = pyautogui.locateOnScreen(f"img/collection/recruitMax.png", minSearchTime=2, region=(500,0,780,1024), confidence=.9)
					if recruitMax:
						print("  See recruitMax | Click | Hiring")
						click(recruitMax)
						sleep(.5)
						self.rightSoft()
					else:
						print("  Don't see recruitMax")
					accept = pyautogui.locateOnScreen(f"img/collection/accept.png", minSearchTime=2, region=(500,0,780,1024), confidence=.9)
					if accept:
						print("  See 'accept' | Click | Hiring")
						click(accept)
						sleep(2.5)
					else:
						print("  Don't see Accept button")
					if self.logHandler("client -> server: 101 wait for: 20"):
						print("  Right LOG | Recruit Succes")
						return True
					barrack = pyautogui.locateOnScreen(f"img/collection/townBarrack.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
					if barrack:
						print("  See fromBarracks | Enter complete")
						return True
					else:
						print("  Don't see fromBarracks")
					if self.clMessageCheckImage():
						continue
				print("    Could not buy an army | FALSE")
				return False
			def exit():
				print("Trying to leave Bastion")
				for _ in range(5):
					barrack = pyautogui.locateOnScreen(f"img/collection/townBarrack.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
					if barrack:
						print("  See fromBarracks | Leave Bastion")
						self.rightSoft()
					else:
						print("  Don't see fromBarracks")
					print("  Search inTheCity")
					inTheCity = pyautogui.locateOnScreen(f"img/collection/inTheCity.png", minSearchTime=2, region=(0,0,1280, 1024), confidence=.85)
					if inTheCity:
						print("    The character is in the city")
						return True
					else:
						print("    Don't see inTheCity")
					if self.clMessageCheckImage():
						continue
				print("  Can't buy. Exit from bastion | FALSE")
				return False
			if enter(unit):
				if exit():
					return True
		if self.openInn():
			if buyUnits(unit):
				return True
	def unitSlotCheck(self, unit):
		print("Unit Slot check")
		firstSquad = pyautogui.locateOnScreen(f"img/collection/squad{unit}.png", minSearchTime=2, region=(0,0,150,230), confidence=.9)
		if firstSquad:
			print(f"  1-st squad contains {unit}")
			return "1"
		secondSquad = pyautogui.locateOnScreen(f"img/collection/squad{unit}.png", minSearchTime=2, region=(0,210,150,280), confidence=.9)
		if secondSquad:
			print(f"  2-nd squad contains {unit}")
			return "2"
		print(f"  No squad contains {unit}")
		return False
	def recognizeTheNumber(self, unit):
		print("Recognize the number of units | Unit Slot check")
		for _ in range(3):
			firstSquad = pyautogui.locateOnScreen(f"img/collection/squad{unit}.png", minSearchTime=2, region=(0,0,150,230), confidence=.9)
			if firstSquad:
				print(f"  1-st squad contains {unit}")
				self.startX, self.startY = firstSquad[0], firstSquad[1]
				pyautogui.screenshot(region=(self.startX + 18, self.startY + 32, 40, 18)).save("unitNumber.png")
				sleep(.5)
				text = recognize('unitNumber.png')
				print(f"  We have {text} {unit}(s)")
				return text
			secondSquad = pyautogui.locateOnScreen(f"img/collection/squad{unit}.png", minSearchTime=2, region=(0,210,150,280), confidence=.9)
			if secondSquad:
				print(f"  2-nd squad contains {unit}")
				self.startX, self.startY = secondSquad[0], secondSquad[1]
				pyautogui.screenshot(region=(self.startX + 18, self.startY + 32, 40, 18)).save("unitNumber.png")
				sleep(.5)
				text = recognize('unitNumber.png')
				print(f"  We have {text} {unit}(s)")
				return text
			self.clMessageCheckImage()
		print(f"    No squad contains {unit} | FALSE")
		return False
	def disbandOneUnit(self, unit):
		print("Trying to disband one unit")
		for _ in range(3):
			self.leftSoft()
			buttonArmy = pyautogui.locateOnScreen(f"img/collection/buttonArmy.png", minSearchTime=2, region=(0,0,780,1024), confidence=.94)
			if buttonArmy:
				print("  See buttonArmy | Click")
				click(buttonArmy)
			else:
				print("  Don't see buttonArmy")
			equipmentSelection = pyautogui.locateOnScreen(f"img/collection/equipmentSelection.png", minSearchTime=2, region=(0,0,680,1024), confidence=.85)
			if equipmentSelection:
				print("  See the equipment selection | Select the desired squad and disband")
				usl = self.unitSlotCheck(unit)
				if usl == "1":
					print("    click 2nd squad | Disband")
					pyautogui.doubleClick(45, 250)
				elif usl == "2":
					print("    click 1st squad | Disband")
					pyautogui.doubleClick(45, 200)
				plusMinus = pyautogui.locateOnScreen(f"img/collection/plusMinus.png", minSearchTime=2, region=(700,0,580,1024), confidence=.92)
				if plusMinus:
					print("    See plusMinus | disband ")
					self.rightSoft()
					disband = pyautogui.locateOnScreen(f"img/collection/disband.png", minSearchTime=2, region=(500,0,780,1024), confidence=.92)
					if disband:
						print("      See disband | Click ")
						click(disband)
						press('enter', presses=2)
					else:
						print("      Don't see Disband")
				else:
					print("    Don't see plusMinus ")
				if self.logHandler("client -> server: 144 wait for: 0"):
					return True
				emptySquad = pyautogui.locateOnScreen(f"img/collection/emptySquad.png", minSearchTime=2, region=(0,0,300,300), confidence=.92)
				if emptySquad:
					print("    See Empty squad | Disband 1 unit Successful")
					return True
				else:
					print("    Don't see emptySquad")
			if self.clMessageCheckImage():
				continue
		print("  Disband 1 unit Failed | FALSE")
		return False
	def step2Verify(self):
		print("Recognize the number of separable units")
		pyautogui.screenshot(region=(self.startX + 10, self.startY + 16, 40, 17)).save("separableUnits.png")
		sleep(.5)
		text = recognize('separableUnits.png')
		print(f"  We have {text} separable units")
		return text
	def badPress(self, unitsCount):
		print("run badPress function")
		for _ in range(3):
			separated = self.step2Verify()
			if separated:
				if int(separated) == unitsCount:
					print("  Verification into badPress was successful")
					return True
				else:
					sepDiffrence = unitsCount - int(separated)
					vert = abs(sepDiffrence % 10)
					horiz = abs(sepDiffrence // 10)
					if sepDiffrence > 0:
						for _ in range(vert):
							press('up')
							sleep(.01)
						for _ in range(horiz):
							press('right')
							sleep(.01)
					elif sepDiffrence < 0:
						for _ in range(vert):
							press('down')
							sleep(.01)
						for _ in range(horiz):
							press('left')
							sleep(.01)
			else:
				print("  SEPARATED UNITS RECOGNIZE FAILED")
			print("  sleep 1 sec")
			sleep(1)
		print("    BADPRESS FAILED | FALSE")
		return False
	def divideIntoSquads(self, unitsCount, unit = "Dragon", squadsCount = 5):
		self.send_message("Divide squads", self.token2)
		righrPrs = unitsCount // 10
		upPrs = unitsCount % 10
		print(f"  Right presses = {righrPrs} | Up presses = {upPrs}")
		def firstSquad():
			self.send_message("First squad", self.token2)
			if self.moveToFirstSlot():
				for k in range(3):
					if k == 0:
						press("up", presses=upPrs, interval = .01)
						press("right", presses=righrPrs, interval = .01)
						sleep(1)
					if unitsCount > 100:
						if self.badPress(unitsCount):
							divide = pyautogui.locateOnScreen(f"img/collection/divide.png", minSearchTime=2, region=(0,0,780,1024), confidence=.92)
							if divide:
								print("  See Divide button | Click")
								click(divide)
								sleep(1)
							else:
								print("  DON'T SEE 'DIVIDE'")
							if self.logHandler("client -> server: 147 wait for: 20"):
								self.send_message("  Divide Log right | 1st squad was separated successfully", self.token2)
								return True
					else:
						divide = pyautogui.locateOnScreen(f"img/collection/divide.png", minSearchTime=2, region=(0,0,780,1024), confidence=.92)
						if divide:
							print("  See Divide button | Click")
							click(divide)
							sleep(.5)
						else:
							print("  DON'T SEE 'DIVIDE'")
						if self.logHandler("client -> server: 147 wait for: 20"):
							self.send_message("  Divide Log right | 1st squad was separated successfully", self.token2)
							return True
					if self.clMessageCheckImage():
						continue
				self.send_message("    FIRST SQUAD DIVIDE FAILED", self.token2)
		def otherSquads():
			self.send_message("Separate other Squads", self.token2)
			for k in range(2, squadsCount):
				for _ in range(3):
					click(45, 195)
					divideSellected = pyautogui.locateOnScreen(f"img/collection/divideSellected.png", minSearchTime=2, region=(0,0,780,1024), confidence=.92)
					if divideSellected:
						print("  See 'Divide Sellected' | Click")
						for m in range(3):
							click(divideSellected)
							plusMinus = pyautogui.locateOnScreen(f"img/collection/plusMinus.png", minSearchTime=2, region=(700,0,580,1024), confidence=.92)
							if plusMinus:
								print("    See plusMinus | Separate ")
								if m == 0:
									press("up", presses=upPrs, interval = .01)
									press("right", presses=righrPrs, interval = .01)
									sleep(1)
								if unitsCount > 100:
									if self.badPress(unitsCount):
										self.leftSoft()
										sleep(.3)
										divideSellected = pyautogui.locateOnScreen(f"img/collection/divideSellected.png", minSearchTime=2, region=(0,0,780,1024), confidence=.92)
										if divideSellected:
											print("      See 'Divide Sellected' | Click")
											click(divideSellected)
											sleep(.5)
											break
										else:
											print("      STEP 2 | DON'T SEE 'DIVIDE SELLECTED'")
								else:
									self.leftSoft()
									sleep(.3)
									divideSellected = pyautogui.locateOnScreen(f"img/collection/divideSellected.png", minSearchTime=2, region=(0,0,780,1024), confidence=.92)
									if divideSellected:
										print("      See 'Divide Sellected' | Click")
										click(divideSellected)
										sleep(.5)
										break
									else:
										print("      STEP 2 | DON'T SEE 'DIVIDE SELLECTED'")
							else:
								print("    DON'T SEE PLUS-MINUS")
							if self.clMessageCheckImage():
								continue
					else:
						print("  STEP 1 | DON'T SEE 'DIVIDE SELLECTED'")
					if self.logHandler("client -> server: 147 wait for: 20"):
						print("  Divide Log right")
						self.send_message(f"  {k} squad was separated successfully", self.token2)
						break
					if self.clMessageCheckImage():
						continue
			print("    DIVIDE LOOP COMPLETED")
		if firstSquad():
			otherSquads()
	def disbandTheExtraOnes(self, remainCount, unit = "Dragon"):
		self.send_message("Disband the extra units", self.token2)
		def divide():
			print("Divide")
			if self.moveToFirstSlot():
				self.leftSoft()
				recognized = self.recognizeTheNumber(unit)
				if recognized:
					diffrence = int(recognized) - remainCount
					righrPrs = diffrence // 10
					upPrs = diffrence % 10
					print(f"  Right presses = {righrPrs} | Up presses = {upPrs}")
					if diffrence <= 0:
						print(f"    The number of units is not enough | Can't disband {diffrence} {unit}(s)")
						return "DONT"
					else:
						print(f"    Need disband {diffrence} {unit}(s)")
						for k in range(3):
							if k == 0:
								click(45, 195)
								press("up", presses=upPrs, interval = .01)
								press("right", presses=righrPrs, interval = .01)
							if self.badPress(diffrence):
								divide = pyautogui.locateOnScreen(f"img/collection/divide.png", minSearchTime=2, region=(0,0,780,1024), confidence=.92)
								if divide:
									print("      See Divide button | Click")
									click(divide)
									sleep(1)
								else:
									print("      DON'T SEE 'DIVIDE'")
								if self.logHandler("client -> server: 147 wait for: 20"):
									self.send_message("      Divide Log right | squad was separated successfully", self.token2)
									return "TRUE"
							if self.clMessageCheckImage():
								continue
						print("    DIVIDE FAILED")
				else:
					print("  RECOGNIZE FAILED")
		def checkRemain():
			print("Check remained units")
			for _ in range(3):
				recognized = self.recognizeTheNumber(unit)
				if recognized:
					if int(recognized) == remainCount:
						print(f"  1-st squad contains needed {remainCount} {unit}(s) | Check successful")
						return True
					else:
						print(f"  {recognized} is not equals to {remainCount} | FAILED")
				else:
					print("    RECOGNIZE FAILED")
				self.clMessageCheckImage()
			print("  REMAINED CHECK FAILED | FALSE")
			return False
		def disband():
			print("Disband the extra units | click 2nd squad | Disband")
			for _ in range(3):
				pyautogui.doubleClick(45, 250)
				self.rightSoft()
				disband = pyautogui.locateOnScreen(f"img/collection/disband.png", minSearchTime=2, region=(500,0,780,1024), confidence=.92)
				if disband:
					print("  See disband | Click ")
					click(disband)
					press('enter', presses=1)
				else:
					print("  Don't see Disband")
				if self.logHandler("client -> server: 144 wait for: 0"):
					print("  Disband extra squad Successful")
					return True
				emptySquad = pyautogui.locateOnScreen(f"img/collection/emptySquad.png", minSearchTime=2, region=(0,0,300,300), confidence=.92)
				if emptySquad:
					print("  See Empty squad | Disband extra squad Successful")
					return True
				else:
					print("  Don't see emptySquad")
				self.clMessageCheckImage()
			print("    DISBAND EXTRA SQUAD FAILED | FALSE")
			return False
		for _ in range(3):
			action = divide()
			if action == "TRUE":
				if checkRemain():
					if disband():
						return True
			elif action == 'DONT':
				return True
		print("    DISBAND EXTRA UNITES FAILED | FALSE")
		return False
	def leaveTheCity(self):
		print("Leaving the city")
		for _ in range(4):
			cityGate = pyautogui.locateOnScreen(f"img/collection/cityGate.png", minSearchTime=2, region=(0,0,1280, 1024), confidence=.92)
			if cityGate:
				print("  See City Gate | Click")
				click(cityGate)
				sleep(.3)
			else:
				print("  Don't see City Gate")
				self.rightSoft()
			if self.logHandler("client -> server: 104 wait for: 0"):
				print("  Exit from the city is successful")
				return True
			if self.clMessageCheckImage():
				continue
		print("    LEAVING THE CITY FAILED | FALSE")
		return False
	def coordinatesCheck(self, x, y):
		print("Compare the current coordinates with the required ones")
		currentCoors = self.logWalkHandler()
		if currentCoors:
			if len(currentCoors) >= 2 and currentCoors[0].isdigit() and currentCoors[1].isdigit():
				currentX, currentY = currentCoors[0], currentCoors[1]
				if int(currentX) == x and int(currentY) == y:
					print("  The coordinates are the same")
					return True
				else:
					print(f"  Current coordinates {currentX}, {currentY} do not match the required {x}, {y}")
					return False
			else:
				print("Current coordinates have wrong format")
				return False
		else:
			print("    Can't get current coordinates | FALSE")
			return False
	def timeCoorsCheck(self, x, y, timeLimit):
		start_time = time.time()
		while True:
			with open(log_file_path, 'r') as file:
				file = file.read()
			position = file.rfind("client -> server: 61 wait for: 0")
			if position != -1:
				heroCoors = file[position - 7:position].replace(')', '').replace('(', '').replace('t', '').replace('c', '').split()
				print("  ", heroCoors)
				if heroCoors[0].isdigit() and heroCoors[1].isdigit():
					if int(heroCoors[0]) == x and int(heroCoors[1]) == y:
						print("    Time CHECK | coordinates match | Succes")
						self.endingIndex = position
						return True
				else:
					print("    coordinates are not digit")
			if time.time() - start_time > timeLimit:
				print(f"  {timeLimit} seconds are up | coordinates do not match")
				return False
			sleep(.25)
	def searchBattle(self):
		print("Search Battle...")
		for _ in range(3):
			battle = pyautogui.locateOnScreen(f"img/collection/battleField.png", minSearchTime=2, region=(0,0,600,400), confidence=.9)
			if battle:
				self.battleNumber += 1
				if random.randint(1, 3) == 3:
					self.send_message(f"  Battle {self.battleNumber} started", self.token2)
				return True
			if self.clMessageCheckImage():
				continue
		print("NO BATTLE | FALSE")
		return False
	def combat(self, myUnit = "Dragon", enemyUnit = "Dragon", magicSpell = "BlindingLight"):
		print("Run Combat Method")
		moveNumber = 1
		if self.joinedBots < 1:
			myUnit = self.startUnit
		def useMagic(onTheEnemy = True, spell = magicSpell, ready = None):
			print("Use Magic")
			for _ in range(3):
				self.rightSoft()
				buttonMagic = pyautogui.locateOnScreen(f"img/collection/buttonMagic.png", minSearchTime=2, region=(500,0,780,1024), confidence=.9)
				if buttonMagic:
					print("  Found buttonMagic | Click")
					click(buttonMagic)
					for _ in range(3):
						magic = pyautogui.locateOnScreen(f"img/collection/magic{spell}.png", minSearchTime=2, region=(0,0,200,1000), confidence=.94)
						if magic:
							print("    See the necessary spell | DoubleClick | click ApplyButton", end = " | ")
							pyautogui.doubleClick(magic)
							for _ in range(3):
								if spell in "PowerOfDeath".split():
									for _ in range(3):
										click(ready)
										sleep(.5)
										applyMagic = pyautogui.locateCenterOnScreen(f"img/collection/applyMagic.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
										if applyMagic:
											print("      Found Apply Magic | Click")
											click(applyMagic[0], applyMagic[1] - 100)
											for _ in range(3):
												sleep(1)
												if self.logHandler("client -> server: 122 wait for: 0"):
													print("        The use of magic is successful")
													return True
											print("      EXCEPTION M5")
										else:
											print("      Don't see APPLY MAGIC")
									print("    EXCEPTION M4")
								enemy = pyautogui.locateOnScreen(f"img/collection/enemy{enemyUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
								if enemy:
									print("    Found enemy | Click | Search Apply Magic")
									click(enemy)
									sleep(.5)
									for _ in range(3):
										applyMagic = pyautogui.locateCenterOnScreen(f"img/collection/applyMagic.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
										if applyMagic:
											print("      Found Apply Magic | Click")
											click(applyMagic[0], applyMagic[1] - 100)
											for _ in range(3):
												sleep(1)
												if self.logHandler("client -> server: 122 wait for: 0"):
													print("        The use of magic is successful")
													return True
											print("      EXCEPTION M5")
										else:
											print("      Don't see APPLY MAGIC")
									print("    EXCEPTION M4")
								else:
									print("    Don't see ENEMY")
							print("  EXCEPTION M3")
						else:
							print("  Don't see NECESSARY SPELL")
					print("    EXCEPTION M2")
				else:
					print("    Don't see MAGIC BUTTON")
			print("  EXCEPTION M1")
		print("  Search Ready")
		for _ in range(10):
			ready = pyautogui.locateOnScreen(f"img/collection/ready{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
			if ready:
				print(f"    Found ready {myUnit} | Search enemy")
				succes = False
				for _ in range(3):
					enemy = pyautogui.locateOnScreen(f"img/collection/enemy{enemyUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
					if enemy:
						print("      Found enemy")
						if moveNumber < 2:
							print("        First Move", end=' | ')
							if useMagic(ready = ready):
								succes = False
								for _ in range(3):
									ready = pyautogui.locateOnScreen(f"img/collection/ready{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
									if ready:
										print("          see ready after Magic | Click enemy")
										click(enemy)
										sleep(2.5)
										if self.logHandler("client -> server: 111 wait for: 0"):
											print("1st move | hit successfully")
											moveNumber += 1
											succes = True
											break
									else:
										print("          Don't see READY AFTER MAGIC")
								if succes:
									break
								else:
									print("        EXCEPTION C2")
						else:
							print("        Not first Move | Click enemy")
							click(enemy)
							if self.logHandler("client -> server: 111 wait for: 0"):
								print(f"          {moveNumber} move | hit successfully")
								succes = True
								moveNumber += 1
								sleep(1)
								break
							elif self.logHandler("client -> server: 113 wait for: 0"):
								print(f"          {moveNumber} move | LAST hit successfully")
								succes = True
								moveNumber += 1
								sleep(1)
								break
					else:
						print("      Don't see ENEMY")
				if self.logHandler("server -> client: 114"):
					print("    The battle is completed successfully")
					sleep(2.5)
					self.leftSoft()
					return True
				if not succes:
					print("    EXCEPTION C1")
			else:
				print("    Not found Ready")
				if self.logHandler("server -> client: 114"):
					print("      The battle is completed successfully")
					sleep(2.5)
					self.leftSoft()
					return True
				notReady = pyautogui.locateOnScreen(f"img/collection/notReady{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
				if notReady:
					print(f"    See notReady {myUnit}| Click")
					click(notReady)
				else:
					print("    Don't see notReady")
				if self.clMessageCheckImage():
					continue

			sleep(1.5)
		print("  EXXXCEPTION COMBAT | MORE THAN 10 MOVES")
	def combatFarm(self, myUnit = "Gunner", enemyUnit = "Troll", magicSpell = "PowerOfDeath", magic = True):
		print("Run CombatFarm Method")
		moveNumber = 1
		def useMagic(onTheEnemy = True, spell = magicSpell, ready = None, magic = magic):
			if magic:
				print("Use Magic")
				for _ in range(3):
					self.rightSoft()
					buttonMagic = pyautogui.locateOnScreen(f"img/collection/buttonMagic.png", minSearchTime=2, region=(500,0,780,1024), confidence=.9)
					if buttonMagic:
						print("  Found buttonMagic | Click")
						click(buttonMagic)
						for _ in range(3):
							magic = pyautogui.locateOnScreen(f"img/collection/magic{spell}.png", minSearchTime=2, region=(0,0,200,1000), confidence=.94)
							if magic:
								print("    See the necessary spell | DoubleClick | click ApplyButton")
								pyautogui.doubleClick(magic)
								for _ in range(3):
									if spell in "PowerOfDeath".split():
										for _ in range(3):
											click(ready)
											sleep(.5)
											applyMagic = pyautogui.locateCenterOnScreen(f"img/collection/applyMagic.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
											if applyMagic:
												print("      Found Apply Magic | Click")
												click(applyMagic[0], applyMagic[1] - 100)
												for _ in range(3):
													sleep(1)
													if self.logHandler("client -> server: 122 wait for: 0"):
														print("        The use of magic is successful")
														return True
												print("      EXCEPTION M5")
											else:
												print("      Don't see APPLY MAGIC")
										print("    EXCEPTION M4")
									enemy = pyautogui.locateOnScreen(f"img/collection/enemy{enemyUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
									if enemy:
										print("    Found enemy | Click | Search Apply Magic")
										click(enemy)
										sleep(.5)
										for _ in range(3):
											applyMagic = pyautogui.locateCenterOnScreen(f"img/collection/applyMagic.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
											if applyMagic:
												print("      Found Apply Magic | Click")
												click(applyMagic[0], applyMagic[1] - 100)
												for _ in range(3):
													sleep(1)
													if self.logHandler("client -> server: 122 wait for: 0"):
														print("        The use of magic is successful")
														return True
												print("      EXCEPTION M5")
											else:
												print("      Don't see APPLY MAGIC")
										print("    EXCEPTION M4")
									else:
										print("    Don't see ENEMY")
								print("    EXCEPTION M3")
							else:
								print("    Don't see NECESSARY SPELL")
						print("  EXCEPTION M2")
					else:
						print("  Don't see MAGIC BUTTON")
				print("    EXCEPTION M1")
			else:
				print("No magic")
				return True
		print("  Search Ready")
		for _ in range(26):
			ready = pyautogui.locateOnScreen(f"img/collection/ready{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
			if ready:
				print(f"    Found ready {myUnit} | Search enemy")
				succes = False
				for _ in range(3):
					enemies = pyautogui.locateAllOnScreen(f"img/collection/enemy{enemyUnit}.png", region=(450,300,370,350), confidence=.94)
					enemyList = list(enemies)
					if enemyList:
						print("      Found enemies")
						if moveNumber < 2:
							print("        First Move")
							if useMagic(ready = ready):
								succes = False
								moveNumber += 1
								for _ in range(3):
									if magic:
										ready = pyautogui.locateOnScreen(f"img/collection/ready{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
									if ready:
										print("          see ready after Magic | Click enemy")
										if len(enemyList) > 1:
											print("Squads more than 1")
											if myUnit == "Necromancer":
												for enemy in enemyList:
													click(enemy)
													sleep(1 + random.randint(2,3)/10)
											else:
												click(enemyList[1])
												sleep(2 + random.randint(0,5)/10)
										else:
											print("Only 1 squad")
											click(enemyList[0])
											if myUnit == "Necromancer":
												sleep(.5)
											else:
												sleep(2 + random.randint(0,5)/10)
										if self.logHandler("client -> server: 113 wait for: 0"):
											print("            1st move | hit successfully | sleep 2")
											moveNumber += 1
											succes = True
											break
									else:
										print("          Don't see READY AFTER MAGIC")
								if succes:
									break
								else:
									print("          EXCEPTION C2")
						else:
							print("        Not first Move | Click enemy")
							if len(enemyList) > 1:
								print("Squads more than 1")
								if myUnit == "Necromancer":
									for enemy in enemyList:
										click(enemy)
										sleep(1 + random.randint(2,3)/10)
								else:
									click(enemyList[1])
									sleep(2 + random.randint(0,5)/10)
							else:
								print("Only 1 squad")
								click(enemyList[0])
								if myUnit == "Necromancer":
									sleep(.5)
								else:
									sleep(2 + random.randint(0,5)/10)
							if self.logHandler("client -> server: 113 wait for: 0"):
								print(f"          {moveNumber} move | hit successfully")
								succes = True
								moveNumber += 1
								break
					else:
						print("      Don't see ENEMIES")
				if self.logHandler("server -> client: 114"):
					print("    The battle is completed successfully")
					sleep(2)
					self.leftSoft()
					return True
				if not succes:
					print("    EXCEPTION C1")
			else:
				print("  Not found Ready")
				if self.logHandler("server -> client: 114"):
					print("    The battle is completed successfully")
					sleep(2)
					self.leftSoft()
					return True
				notReady = pyautogui.locateOnScreen(f"img/collection/notReady{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
				if notReady:
					print(f"    See notReady {myUnit}| Click")
					click(notReady)
				else:
					print("    Don't see notReady")
				if self.clMessageCheckImage():
					continue

			sleep(1.5)
		print("  EXXXCEPTION COMBAT | MORE THAN 25 MOVES")
		return False
	def combatPumpkin(self, myUnit = "Dragon", enemyUnit = "Troll", magicSpell = "PowerOfDeath", magic = True):
		print("Run CombatPumpkin Method")
		moveNumber = 1
		def useMagic(onTheEnemy = True, spell = magicSpell, ready = None, magic = magic):
			if magic:
				print("Use Magic")
				for _ in range(3):
					self.rightSoft()
					buttonMagic = pyautogui.locateOnScreen(f"img/collection/buttonMagic.png", minSearchTime=2, region=(500,0,780,1024), confidence=.9)
					if buttonMagic:
						print("  Found buttonMagic | Click")
						click(buttonMagic)
						for _ in range(3):
							magic = pyautogui.locateOnScreen(f"img/collection/magic{spell}.png", minSearchTime=2, region=(0,0,200,1000), confidence=.94)
							if magic:
								print("    See the necessary spell | DoubleClick | click ApplyButton")
								pyautogui.doubleClick(magic)
								for _ in range(3):
									if spell in "PowerOfDeath".split():
										for _ in range(3):
											click(ready)
											sleep(.5)
											applyMagic = pyautogui.locateCenterOnScreen(f"img/collection/applyMagic.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
											if applyMagic:
												print("      Found Apply Magic | Click")
												click(applyMagic[0], applyMagic[1] - 100)
												for _ in range(3):
													sleep(1)
													if self.logHandler("client -> server: 122 wait for: 0"):
														print("        The use of magic is successful")
														return True
												print("      EXCEPTION M5")
											else:
												print("      Don't see APPLY MAGIC")
										print("    EXCEPTION M4")
									enemy = pyautogui.locateOnScreen(f"img/collection/enemy{enemyUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
									if enemy:
										print("    Found enemy | Click | Search Apply Magic")
										click(enemy)
										sleep(.5)
										for _ in range(3):
											applyMagic = pyautogui.locateCenterOnScreen(f"img/collection/applyMagic.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
											if applyMagic:
												print("      Found Apply Magic | Click")
												click(applyMagic[0], applyMagic[1] - 100)
												for _ in range(3):
													sleep(1)
													if self.logHandler("client -> server: 122 wait for: 0"):
														print("        The use of magic is successful")
														return True
												print("      EXCEPTION M5")
											else:
												print("      Don't see APPLY MAGIC")
										print("    EXCEPTION M4")
									else:
										print("    Don't see ENEMY")
								print("    EXCEPTION M3")
							else:
								print("    Don't see NECESSARY SPELL")
						print("  EXCEPTION M2")
					else:
						print("  Don't see MAGIC BUTTON")
				print("    EXCEPTION M1")
			else:
				print("No magic")
				return True
		print("  Search Ready")
		for _ in range(10):
			ready = pyautogui.locateOnScreen(f"img/collection/ready{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
			if ready:
				print(f"    Found ready {myUnit} | Search enemy")
				succes = False
				for _ in range(3):
					enemies = pyautogui.locateAllOnScreen(f"img/collection/enemy{enemyUnit}.png", region=(450,300,370,350), confidence=.94)
					enemyList = list(enemies)
					if enemyList:
						print("      Found enemies")
						if moveNumber < 2:
							print("        First Move")
							if useMagic(ready = ready):
								succes = False
								moveNumber += 1
								for _ in range(3):
									ready = pyautogui.locateOnScreen(f"img/collection/ready{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
									if ready:
										print("          see ready after Magic | Click enemy")
										if len(enemyList) == 5:
											print("Equals 5 squads on the 1st move")
											barrier1 = pyautogui.locateOnScreen(f"img/collection/fieldBarrier.png", minSearchTime=1.5, region=(500,380,75,65), confidence=.94)
											if barrier1:
												print("SEE BARIK ONE")
												barrier2 = pyautogui.locateOnScreen(f"img/collection/fieldBarrier.png", minSearchTime=1.5, region=(550,380,75,65), confidence=.94)
												if barrier2:
													print("SEE BARIK TWO")
													click(enemyList[2])
													sleep(2 + random.randint(4,8)/10)
													click(enemyList[1])
													sleep(2 + random.randint(4,8)/10)
												else:
													print("No Barrier 2")
													barrier3 = pyautogui.locateOnScreen(f"img/collection/fieldBarrier.png", minSearchTime=1.5, region=(600,380,75,65), confidence=.94)
													if barrier3:
														print("SEE BARIK THREE")
														click(enemyList[1])
														sleep(2 + random.randint(4,8)/10)
														click(enemyList[0])
														sleep(2 + random.randint(4,8)/10)
														click(enemyList[3])
														sleep(2 + random.randint(4,8)/10)
													else:
														print("No Barrier 3")
														click(enemyList[1])
														sleep(2 + random.randint(4,8)/10)
														click(enemyList[0])
														sleep(2 + random.randint(4,8)/10)
														for k in range(2, 5):
															click(enemyList[k])
															sleep(2 + random.randint(4,8)/10)
											else:
												print("No Barrier 1")
												for i in enemyList:
													click(i)
													sleep(2 + random.randint(4,8)/10)
										else:
											print(f"Not 5 squads | {len(enemyList)} squads")
											if len(enemyList) == 1:
												print("only 1 enemy squad")
												click(enemyList[0])
												sleep(2 + random.randint(0,5)/10)
											elif len(enemyList) >  1:
												print("More 1 enemy squads")
												for i in enemyList:
													click(i)
													sleep(2 + random.randint(4,8)/10)
										if self.logHandler("client -> server: 111 wait for: 0"):
											print("            1st move | hit successfully | sleep 2")
											moveNumber += 1
											succes = True
											break
										if self.logHandler("client -> server: 113 wait for: 0"):
											print("          Last hit successfully | sleep 2")
											moveNumber += 1
											succes = True
											break
									else:
										print("          Don't see READY AFTER MAGIC")
								if succes:
									break
								else:
									print("          EXCEPTION C2")
						else:
							print("        Not first Move | Click enemy")
							if len(enemyList) == 5:
								print("Equals 5 squads on the 1st move")
								barrier1 = pyautogui.locateOnScreen(f"img/collection/fieldBarrier.png", minSearchTime=1.5, region=(500,380,75,65), confidence=.94)
								if barrier1:
									print("SEE BARIK ONE")
									barrier2 = pyautogui.locateOnScreen(f"img/collection/fieldBarrier.png", minSearchTime=1.5, region=(550,380,75,65), confidence=.94)
									if barrier2:
										print("SEE BARIK TWO")
										click(enemyList[2])
										sleep(2 + random.randint(4,8)/10)
										click(enemyList[1])
										sleep(2 + random.randint(4,8)/10)
									else:
										barrier3 = pyautogui.locateOnScreen(f"img/collection/fieldBarrier.png", minSearchTime=1.5, region=(600,380,75,65), confidence=.94)
										if barrier3:
											print("SEE BARIK THREE")
											click(enemyList[1])
											sleep(2 + random.randint(4,8)/10)
											click(enemyList[0])
											sleep(2 + random.randint(4,8)/10)
											click(enemyList[3])
											sleep(2 + random.randint(4,8)/10)
										else:
											click(enemyList[0])
											sleep(2 + random.randint(4,8)/10)
							else:
								print("Not 5 squads")
								click(enemyList[0])
								sleep(2 + random.randint(0,5)/10)
							if self.logHandler("client -> server: 111 wait for: 0"):
								print("             hit successfully | sleep 2")
								moveNumber += 1
								succes = True
								break
							if self.logHandler("client -> server: 113 wait for: 0"):
								print("          Last hit successfully | sleep 2")
								moveNumber += 1
								succes = True
								break
					else:
						print("      Don't see ENEMIES")
				if self.logHandler("server -> client: 114"):
					print("    The battle is completed successfully")
					sleep(1.5)
					self.leftSoft()
					return True
				if not succes:
					print("    EXCEPTION C1")
			else:
				print("  Not found Ready")
				if self.logHandler("server -> client: 114"):
					print("    The battle is completed successfully")
					sleep(1.5)
					self.leftSoft()
					return True
				notReady = pyautogui.locateOnScreen(f"img/collection/notReady{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
				if notReady:
					print(f"    See notReady {myUnit}| Click")
					click(notReady)
				else:
					print("    Don't see notReady")
				if self.clMessageCheckImage():
					continue
			sleep(1.5)
		print("  EXXXCEPTION COMBAT | MORE THAN 10 MOVES")
	def combatSimple(self, enemyUnit = "Troll"):
		print("Run Combat Simple Method")
		moveNumber = 1
		for _ in range(15):
			timeBefor = time.time()
			enemies = pyautogui.locateAllOnScreen(f"img/collection/enemy{enemyUnit}.png", region=(300,300,370,350), confidence=.94)
			enemyList = list(enemies)
			if enemyList:
				print("      Found enemies")
				for _ in range(25):
					if moveNumber > 1:
						enemies = pyautogui.locateAllOnScreen(f"img/collection/enemy{enemyUnit}.png", region=(300,300,370,350), confidence=.94)
					if enemyList:
						if len(enemyList) > 1:
							print("Squads more than 1")
							if moveNumber > 1:
								if moveNumber > 5:
									while time.time() <= (timeBefor + random.randint(1,2)/10):
										sleep(.05)	
								else:
									while time.time() <= (timeBefor + 1 + random.randint(1,2)/10):
										sleep(.05)
							timeBefor = time.time()
							click(enemyList[1])
							click(enemyList[0])
							pyautogui.moveTo(100, 100)
							moveNumber += 1
							enemyList = list(enemies)
						else:
							print("Only 1 squad")
							if moveNumber > 1:
								if moveNumber > 5:
									while time.time() <= (timeBefor + random.randint(1,2)/10):
										sleep(.05)	
								else:
									while time.time() <= (timeBefor + 1 + random.randint(1,2)/10):
										sleep(.05)
							timeBefor = time.time()
							click(enemyList[0])
							pyautogui.moveTo(100, 100)
							moveNumber += 1
							enemyList = list(enemies)
						if self.logHandler("server -> client: 114"):
							print("    The battle is completed successfully")
							sleep(1)
							clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
							if clanMessage:
								self.leftSoft()
							return True
					else:
						print("      Don't see ENEMIES")
						enemyList = list(enemies)
						sleep(.3)
						if self.logHandler("server -> client: 114"):
							print("    The battle is completed successfully")
							sleep(1)
							clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
							if clanMessage:
								self.leftSoft()
							return True
			else:
				print("      Don't see ENEMIES")
			if self.logHandler("server -> client: 114"):
				print("    The battle is completed successfully")
				sleep(1)
				clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
				if clanMessage:
					self.leftSoft()
				return True
			if self.clMessageCheckImage():
				continue
		if self.logHandler("server -> client: 114"):
			print("    The battle is completed successfully")
			sleep(1)
			clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
			if clanMessage:
				self.leftSoft()
			return True
		print("  EXXXCEPTION COMBAT | MORE THAN 50 MOVES")
		return False
	def combatMix(self, enemyUnit = "Troll"):
		print("Run Combat Mix Method")
		moveNumber, shotCounter, secodMagic = 1, 0, False
		def useMagic(squad = 1):
			print("Use Magic")
			for _ in range(3):
				self.rightSoft()
				buttonMagic = pyautogui.locateOnScreen(f"img/collection/buttonMagic.png", minSearchTime=2, region=(350,0,780,1024), confidence=.9)
				if buttonMagic:
					print("  Found buttonMagic | Click")
					click(buttonMagic)
					sleep(.3)
					self.leftSoft()
					for _ in range(3):
						sleep(.3)
						if squad == 1:
							click(380, 585)
						elif squad == 2:
							click(430, 585)
						applyMagic = pyautogui.locateCenterOnScreen(f"img/collection/applyMagic.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
						if applyMagic:
							print("      Found Apply Magic | Click")
							click(applyMagic[0], applyMagic[1] - 100)
							for _ in range(3):
								sleep(1)
								if self.logHandler("client -> server: 122 wait for: 0"):
									print("        The use of magic is successful")
									return True
						else:
							print("      Don't see APPLY MAGIC")
				else:
					print("  Don't see MAGIC BUTTON")
				if self.logHandler("client -> server: 122 wait for: 0"):
					print("        The use of magic is successful")
					return True
			print("    USE MAGIC FAILED | FALSE")
			return False
		for _ in range(15):
			timeBefor = time.time()
			enemies = pyautogui.locateAllOnScreen(f"img/collection/enemy{enemyUnit}.png", region=(300,300,370,350), confidence=.94)
			enemyList = list(enemies)
			if enemyList:
				print("  Found Trolls")
				camels = pyautogui.locateAllOnScreen(f"img/collection/enemyCamel.png", region=(300,300,370,350), confidence=.94)
				camelList = list(camels)
				if camelList:
					if shotCounter == 0 and moveNumber == 1:
						useMagic(1)
					if shotCounter > 4:
						if not secodMagic and useMagic(2):
							secodMagic = True
				for _ in range(25):
					if moveNumber > 1:
						enemies = pyautogui.locateAllOnScreen(f"img/collection/enemy{enemyUnit}.png", region=(300,300,370,350), confidence=.94)
					if enemyList:
						if len(enemyList) > 1:
							print("Squads more than 1")
							if moveNumber > 1:
								while time.time() <= (timeBefor + 1 + random.randint(1,2)/10):
									sleep(.05)
							timeBefor = time.time()
							click(enemyList[1])
							click(enemyList[0])
							pyautogui.moveTo(100, 100)
							moveNumber += 1
							enemyList = list(enemies)
						else:
							print("Only 1 squad")
							if moveNumber > 1:
								while time.time() <= (timeBefor + 1 + random.randint(1,2)/10):
									sleep(.05)
							timeBefor = time.time()
							click(enemyList[0])
							pyautogui.moveTo(100, 100)
							moveNumber += 1
							enemyList = list(enemies)
						if self.logHandler("client -> server: 113 wait for: 0"):
							print("          hit successfully")
							shotCounter += 1
						if self.logHandler("server -> client: 114"):
							print("    The battle is completed successfully")
							sleep(1.5)
							clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
							if clanMessage:
								self.leftSoft()
							return True
					else:
						camels = pyautogui.locateAllOnScreen(f"img/collection/enemyCamel.png", region=(300,300,370,350), confidence=.94)
						camelList = list(camels)
						if camelList:
							print("See Camels")
							if shotCounter > 5:
								if not secodMagic and useMagic(2):
									secodMagic = True
							enemies = pyautogui.locateAllOnScreen(f"img/collection/enemy{enemyUnit}.png", region=(300,300,370,350), confidence=.94)
							if len(camelList) > 1:
								print("Camels more than 1")
								timeBefor = time.time()
								click(camelList[1])
								click(camelList[0])
								pyautogui.moveTo(100, 100)
								moveNumber += 1
								enemyList = list(enemies)
							else:
								print("Only 1 squad Camel")
								timeBefor = time.time()
								click(camelList[0])
								pyautogui.moveTo(100, 100)
								moveNumber += 1
								enemyList = list(enemies)
							if self.logHandler("client -> server: 113 wait for: 0"):
								print("          hit successfully")
								shotCounter += 1
						sleep(.3)
						enemyList = list(enemies)
						if self.logHandler("server -> client: 114"):
							print("    The battle is completed successfully")
							sleep(1.5)
							clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
							if clanMessage:
								self.leftSoft()
							return True
			else:
				print("      Don't see Trolls")
				camels = pyautogui.locateAllOnScreen(f"img/collection/enemyCamel.png", region=(300,300,370,350), confidence=.94)
				camelList = list(camels)
				if camelList:
					print("See Camels")
					if shotCounter > 5:
						if not secodMagic and useMagic(2):
							secodMagic = True
					enemies = pyautogui.locateAllOnScreen(f"img/collection/enemy{enemyUnit}.png", region=(300,300,370,350), confidence=.94)
					if len(camelList) > 1:
						print("Camels more than 1")
						timeBefor = time.time()
						click(camelList[1])
						click(camelList[0])
						pyautogui.moveTo(100, 100)
						moveNumber += 1
						enemyList = list(enemies)
					else:
						print("Only 1 squad Camel")
						timeBefor = time.time()
						click(camelList[0])
						pyautogui.moveTo(100, 100)
						moveNumber += 1
						enemyList = list(enemies)
					if self.logHandler("client -> server: 113 wait for: 0"):
						print("          hit successfully")
						shotCounter += 1
					if self.logHandler("server -> client: 114"):
						print("    The battle is completed successfully")
						sleep(1)
						clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
						if clanMessage:
							self.leftSoft()
						return True
			if self.logHandler("server -> client: 114"):
				print("    The battle is completed successfully")
				sleep(1.5)
				clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
				if clanMessage:
					self.leftSoft()
				return True
			if self.clMessageCheckImage():
				continue
		if self.logHandler("server -> client: 114"):
			print("    The battle is completed successfully")
			sleep(1.5)
			clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
			if clanMessage:
				self.leftSoft()
			return True
		print("  EXXXCEPTION COMBAT | MORE THAN 50 MOVES")
		return False
	def combatCamel(self, enemyUnit = "Camel"):
		print("Run Combat Camel Method")
		moveNumber, shotCounter, secodMagic = 1, 0, False
		def useMagic(squad = 1):
			print("Use Magic")
			for _ in range(3):
				self.rightSoft()
				buttonMagic = pyautogui.locateOnScreen(f"img/collection/buttonMagic.png", minSearchTime=2, region=(350,0,780,1024), confidence=.9)
				if buttonMagic:
					print("  Found buttonMagic | Click")
					click(buttonMagic)
					sleep(.3)
					self.leftSoft()
					sleep(.3)
					for _ in range(1):
						if squad == 1:
							click(380, 585)
						elif squad == 2:
							click(430, 585)
						applyMagic = pyautogui.locateCenterOnScreen(f"img/collection/applyMagic.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
						if applyMagic:
							print("      Found Apply Magic | Click")
							click(applyMagic[0], applyMagic[1] - 100)
							for _ in range(3):
								sleep(1)
								if self.logHandler("client -> server: 122 wait for: 0"):
									print("        The use of magic is successful")
									return True
						else:
							print("      Don't see APPLY MAGIC")
				else:
					print("  Don't see MAGIC BUTTON")
				if self.logHandler("client -> server: 122 wait for: 0"):
					print("        The use of magic is successful")
					return True
			print("    USE MAGIC FAILED | FALSE")
			return False
		for _ in range(15):
			timeBefor = time.time()
			enemies = pyautogui.locateAllOnScreen(f"img/collection/enemy{enemyUnit}.png", region=(300,300,370,350), confidence=.94)
			enemyList = list(enemies)
			if enemyList:
				print(f"  Found {enemyUnit}s")
				for _ in range(25):
					if moveNumber > 1:
						enemies = pyautogui.locateAllOnScreen(f"img/collection/enemy{enemyUnit}.png", region=(300,300,370,350), confidence=.94)
					if shotCounter == 0 and moveNumber == 1:
						useMagic(1)
					if shotCounter > 2:
						if not secodMagic and useMagic(2):
							secodMagic = True
					if enemyList:
						if len(enemyList) > 1:
							print("Squads more than 1")
							if moveNumber > 1:
								while time.time() <= (timeBefor + random.randint(1,2)/10):
									sleep(.05)
							timeBefor = time.time()
							click(enemyList[1])
							click(enemyList[0])
							pyautogui.moveTo(100, 100)
							moveNumber += 1
							enemyList = list(enemies)
						else:
							print("Only 1 squad")
							if moveNumber > 1:
								while time.time() <= (timeBefor + random.randint(1,2)/10):
									sleep(.05)
							timeBefor = time.time()
							click(enemyList[0])
							pyautogui.moveTo(100, 100)
							moveNumber += 1
							enemyList = list(enemies)
						if self.logHandler("client -> server: 113 wait for: 0"):
							print("          hit successfully")
							sleep(2)
							shotCounter += 1
						if self.logHandler("server -> client: 114"):
							print("    The battle is completed successfully")
							sleep(1)
							clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
							if clanMessage:
								self.leftSoft()
							return True
					else:
						print("      Don't see ENEMIES")
						enemyList = list(enemies)
						sleep(.3)
						if self.logHandler("server -> client: 114"):
							print("    The battle is completed successfully")
							sleep(1.5)
							clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
							if clanMessage:
								self.leftSoft()
							return True
			else:
				print("      Don't see ENEMIES")
			if self.logHandler("server -> client: 114"):
				print("    The battle is completed successfully")
				sleep(1.5)
				clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
				if clanMessage:
					self.leftSoft()
				return True
			if self.clMessageCheckImage():
				continue
		if self.logHandler("server -> client: 114"):
			print("    The battle is completed successfully")
			sleep(1.5)
			clanMessage = pyautogui.locateOnScreen(f"img/collection/clanMessage.png", minSearchTime=3, region=(0,500,1280, 524), confidence=.85)
			if clanMessage:
				self.leftSoft()
			return True
		print("  EXXXCEPTION COMBAT | MORE THAN 50 MOVES")
		return False
	def startMove(self, firstKey = "down"):
		print("Start move ")
		for _ in range(2):
			arrows = (firstKey, 'up', 'left', 'right', "down")
			for arrow in arrows:
				sleep(.3)
				print(f"  Current arrow is {arrow} | press")
				press(arrow)
				walk = pyautogui.locateOnScreen(f"img/collection/walk.png", minSearchTime=2, region=(0,300,780,724), confidence=.92)
				if walk:
					print("    See walkButtn | Click")
					click(walk)
					sleep(.5)
					if self.logWalkHandler():
						print("      StartMove succesful")
						return True
				else:
					print("    Don't  see walkButtn | toCenter")
					self.toCenter()
			if self.clMessageCheckImage():
				continue
		print("startMove FAILED | FALSE")
		return False
	def moveOnMap(self, x, y, npcAttack = True, iters = 3):
		print("Try to move on the map")
		attempts = 0
		for _ in range(iters):
			currentCoors = self.logWalkHandler()
			if currentCoors:
				if len(currentCoors) >= 2 and currentCoors[0].isdigit() and currentCoors[1].isdigit():
					currentX, currentY = currentCoors[0], currentCoors[1]
				else:
					self.startMove()
					continue
				deltaX, deltaY = int(currentX) - x, int(currentY) - y
				print(f"  DeltaX, deltaY - {-deltaX}, {-deltaY}")
				def singleMove(arrow, counterArrow, horizontal = True):
					print(f"Move {arrow} 8-15")
					press(arrow, presses = 15)
					for k in range(7):
						print(f"  Try to move on {15-k} tiles")
						print(f"  Press Counter Arrow - {counterArrow.upper()}")
						press(counterArrow)
						walk = pyautogui.locateOnScreen(f"img/collection/walk.png", minSearchTime=1.5, region=(0,300,780,724), confidence=.92)
						if walk:
							print("    See walkButtn | Click")
							click(walk)
							sleep(2)
							curCoors = self.logWalkHandler()
							if curCoors:
								curX2, curY2 = curCoors[0], curCoors[1]
								if horizontal:
									if currentX != curX2:
										print("      coordinate X was changed. Short step successful")
										return True
								else:
									if currentY != curY2:
										print("      coordinate Y was changed. Short step successful")
										return True
						else:
							print("  Don't  see walkButtn ")
					print("    Loop complete | CAN'T MOVE | FALSE")
					return False
				if abs(deltaX) > 16:
					print("    Horizontal movement is impossible. Try to take shorter steps")
					if deltaX < 0:
						if deltaY < 0:
							for k in range(5):
								if singleMove('right', 'left'):
									break
								if npcAttack:
									if self.logHandler("server -> client: 24"):
										print("      Character was attacked by an npc")
										if self.searchBattle():
											if self.combat():
												continue
								if self.clMessageCheckImage():
									continue
								self.toCenter()
								print("    Press Down")
								press("down", presses = k+1)
								sleep(.5)
						elif deltaY >= 0:
							for k in range(5):
								if singleMove('right', 'left'):
									break
								if npcAttack:
									if self.logHandler("server -> client: 24"):
										print("      Character was attacked by an npc")
										if self.searchBattle():
											if self.combat():
												continue
								if self.clMessageCheckImage():
									continue
								self.toCenter()
								print("Press Up")
								press("up", presses = k+1)
								sleep(.5)
					elif deltaX > 0:
						if deltaY < 0:
							for k in range(5):
								if singleMove('left', 'right'):
									break
								if npcAttack:
									if self.logHandler("server -> client: 24"):
										print("      Character was attacked by an npc")
										if self.searchBattle():
											if self.combat():
												continue
								if self.clMessageCheckImage():
									continue
								self.toCenter()
								print("    Press Down")
								press("down", presses = k+1)
								sleep(.5)
						elif deltaY >= 0:
							for k in range(5):
								if singleMove('left', 'right'):
									break
								if npcAttack:
									if self.logHandler("server -> client: 24"):
										print("      Character was attacked by an npc")
										if self.searchBattle():
											if self.combat():
												continue
								if self.clMessageCheckImage():
									continue
								self.toCenter()
								print("    Press Up")
								press("up", presses = k+1)
								sleep(.5)
					continue
				if abs(deltaY) > 16:
					print("    Vertical movement is impossible.  Try to take shorter steps")
					if deltaY < 0:
						if deltaX < 0:
							for k in range(5):
								if singleMove('down', 'up', horizontal = False):
									break
								if npcAttack:
									if self.logHandler("server -> client: 24"):
										print("      Character was attacked by an npc")
										if self.searchBattle():
											if self.combat():
												continue
								if self.clMessageCheckImage():
									continue
								self.toCenter()
								print("    Press Right")
								press("right", presses = k+1)
								sleep(.5)
						elif deltaX >= 0:
							for k in range(5):
								if singleMove('down', 'up', horizontal = False):
									break
								if npcAttack:
									if self.logHandler("server -> client: 24"):
										print("      Character was attacked by an npc")
										if self.searchBattle():
											if self.combat():
												continue
								if self.clMessageCheckImage():
									continue
								self.toCenter()
								print("    Press Left")
								press("left", presses = k+1)
								sleep(.5)
					elif deltaY > 0:
						if deltaX < 0:
							for k in range(5):
								if singleMove('up', 'down', horizontal = False):
									break
								if npcAttack:
									if self.logHandler("server -> client: 24"):
										print("      Character was attacked by an npc")
										if self.searchBattle():
											if self.combat():
												continue
								if self.clMessageCheckImage():
									continue
								self.toCenter()
								print("    Press Right")
								press("right", presses = k+1)
								sleep(.5)
						elif deltaX >= 0:
							for k in range(5):
								if singleMove('up', 'down', horizontal = False):
									break
								if npcAttack:
									if self.logHandler("server -> client: 24"):
										print("      Character was attacked by an npc")
										if self.searchBattle():
											if self.combat():
												continue
								if self.clMessageCheckImage():
									continue
								self.toCenter()
								print("    Press Left")
								press("left", presses = k+1)
								sleep(.5)
					continue
				if deltaX < 0:
					press('right', presses = abs(deltaX))
				elif deltaX > 0:
					press('left', presses = deltaX)
				if deltaY < 0:
					press('down', presses = abs(deltaY))
				elif deltaY > 0:
					press('up', presses = deltaY)
				walk = pyautogui.locateOnScreen(f"img/collection/walk.png", minSearchTime=2, region=(0,300,780,724), confidence=.92)
				if walk:
					print("    See walkButtn | Click")
					click(walk)
					if self.timeCoorsCheck(x, y, 3):
						print('      The move was successful')
						return True
				else:
					print("    Don't  see walkButtn")
				if self.coordinatesCheck(x, y):
					print('    The move was successful')
					return True
				if npcAttack:
					if self.logHandler("server -> client: 24"):
						print("    Character was attacked by an npc")
						if self.searchBattle():
							if self.combat():
								continue
				if self.clMessageCheckImage():
					self.toCenter()
					continue
				self.startMove()
			else:
				print("  Can't get current coordinates | FALSE")
				return False
			self.toCenter()
			attempts += 1
			print(f"Attempt {attempts} COMPLETED")
		print("    MOVEMENT FAILED | FALSE")
		return False
	def searchBot(self, coorsMatch = True, enemy = "Dragon"):
		print("Looking for bots...")
		bots = pyautogui.locateAllOnScreen(f"img/collection/part{enemy}.png", region=(0, 0, 1280, 1024), confidence=.9)
		botList = list(bots)
		if botList:
			print("  FOUND BOTs")
			if len(botList) >= 2:
				print('    See >= 2 bots')
				botIndex = random.randint(0, len(botList) - 1)
				print(f"    Sellected bot N{botIndex}")
				if botList[botIndex][0] != self.lastBot[0] and botList[botIndex][1] != self.lastBot[1]:
					print("      The bot's coordinates differ from the previous ones | CLICK")
					click(botList[botIndex])
					self.lastBot = botList[botIndex]
				else:
					print("      coordinates match | NOCLICK")
					if not coorsMatch:
						print("        CLICK ANYWAY")
						click(botList[botIndex])
						self.lastBot = botList[botIndex]
			elif len(botList) == 1:
				print('    1 bot')
				if botList[0][0] != self.lastBot[0] and botList[0][1] != self.lastBot[1]:
					print("      The bot's coordinates differ from the previous ones | CLICK")
					click(botList[0])
					self.lastBot = botList[0]
				else:
					print("      coordinates match | NOCLICK")
					if not coorsMatch:
						print("        CLICK ANYWAY")
						click(botList[0])
						self.lastBot = botList[0]
			clickBot = pyautogui.locateCenterOnScreen(f"img/clickBot.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
			if clickBot:
				print("    FOUND click BOT")
				click(clickBot[0], clickBot[1] - 100)
				print("attack ")
				sleep(1)
				self.botListLenght = len(botList)
				return "NICE"
			else:
				print("    Click bot not found")
				return "NOCLICK"
		else:
			print("  dont see boots")
			return 'NOBOTS'
	def searchBotFarm(self, enemy = "Dragon", side = "1", region=(0, 0, 1200, 1200)):
		if side == "1":
			window_center_x, window_center_y = 960, 0
		elif side == "2":
			window_center_x, window_center_y = 0, 1024
		elif side == "3":
			window_center_x, window_center_y = 0, 0
		else:
			window_center_x, window_center_y = 640, 500
		def distance(point1, point2):
			return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
		print("Looking for bots...")
		bots = pyautogui.locateAllOnScreen(f"img/collection/part{enemy}.png", region=region, confidence=.9)
		botList = list(bots)
		if botList:
			print("  FOUND BOTs")
			self.noNPC = 0
			if len(botList) >= 2:
				print('    See >= 2 bots')
				self.npcCount = 2
				sorted_objects = sorted(botList, key=lambda obj: distance((window_center_x, window_center_y), obj))
				closest_objects = sorted_objects[:3]
				if len(botList) == 2:
					if self.farm12 == 1:
						print('Attack first bot')
						click(closest_objects[0])
						self.farm12 = 2
					elif self.farm12 == 2 or self.farm12 == 3:
						print('Attack 2nd bot')
						click(closest_objects[1])
						self.farm12 = 1
				else:
					if self.farm12 == 1:
						print('Attack first bot')
						click(closest_objects[0])
						self.farm12 = 2
					elif self.farm12 == 2:
						print('Attack 2nd bot')
						click(closest_objects[1])
						self.farm12 = 3
					elif self.farm12 == 3:
						print('Attack 3rd bot')
						click(closest_objects[2])
						self.farm12 = 1
			elif len(botList) == 1:
				self.npcCount = 1
				print('    1 bot')
				click(botList[0])
				self.lastBot = botList[0]
			clickBot = pyautogui.locateCenterOnScreen(f"img/clickBot.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
			if clickBot:
				print("    FOUND click BOT")
				click(clickBot[0], clickBot[1] - 100)
				print("attack ")
				sleep(1)
				self.botListLenght = len(botList)
				return "NICE"
			else:
				print("    Click bot not found")
				return "NOCLICK"
		else:
			self.noNPC += 1
			print(f"  Don't see boots {self.noNPC}")
			return 'NOBOTS'
	def moveEnd(self):
		print("Try to click EndTurn")
		for _ in range(3):
			self.rightSoft()
			sleep(.3)
			endTurn = pyautogui.locateOnScreen(f"img/collection/endTurn.png", minSearchTime=2, region=(500,0,780,1024), confidence=.93)
			if endTurn:
				print("  See endTurn | Click")
				click(endTurn)
				sleep(.5)
				if self.logHandler("client -> server: 112 wait for: 0"):
					print("    End Turn pressed successfully")
					return True
			else:
				print("  DON'T SEE END TURN")
		print("END TURN FAILED | FALSE")
		return False
	def combatExtented(self, myUnit = "Dragon", enemyUnit = "Dragon", magicSpell = "BlindingLight"):
		print("Run Combat Extented Method")
		moveNumber = 1
		def useMagic(onTheEnemy = True, spell = magicSpell, ready = None):
			print("Use Magic")
			for _ in range(3):
				self.rightSoft()
				buttonMagic = pyautogui.locateOnScreen(f"img/collection/buttonMagic.png", minSearchTime=2, region=(500,0,780,1024), confidence=.9)
				if buttonMagic:
					print("  Found buttonMagic | Click")
					click(buttonMagic)
					for _ in range(3):
						magic = pyautogui.locateOnScreen(f"img/collection/magic{spell}.png", minSearchTime=2, region=(0,0,200,1000), confidence=.94)
						if magic:
							print("    See the necessary spell | DoubleClick | click ApplyButton")
							pyautogui.doubleClick(magic)
							for _ in range(3):
								if spell in "PowerOfDeath".split():
									for _ in range(3):
										click(ready)
										sleep(.5)
										applyMagic = pyautogui.locateCenterOnScreen(f"img/collection/applyMagic.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
										if applyMagic:
											print("      Found Apply Magic | Click")
											click(applyMagic[0], applyMagic[1] - 100)
											for _ in range(3):
												sleep(1)
												if self.logHandler("client -> server: 122 wait for: 0"):
													print("        The use of magic is successful")
													return True
											print("      EXCEPTION M5")
										else:
											print("      Don't see APPLY MAGIC")
									print("    EXCEPTION M4")
								enemy = pyautogui.locateOnScreen(f"img/collection/enemy{enemyUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
								if enemy:
									print("    Found enemy | Click | Search Apply Magic")
									click(enemy)
									sleep(.5)
									for _ in range(3):
										applyMagic = pyautogui.locateCenterOnScreen(f"img/collection/applyMagic.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
										if applyMagic:
											print("      Found Apply Magic | Click")
											click(applyMagic[0], applyMagic[1] - 100)
											for _ in range(3):
												sleep(1)
												if self.logHandler("client -> server: 122 wait for: 0"):
													print("        The use of magic is successful")
													return True
											print("      EXCEPTION M5")
										else:
											print("      Don't see APPLY MAGIC")
									print("    EXCEPTION M4")
								else:
									print("    Don't see ENEMY")
							print("    EXCEPTION M3")
						else:
							print("    Don't see NECESSARY SPELL")
					print("  EXCEPTION M2")
				else:
					print("  Don't see MAGIC BUTTON")
			print("    EXCEPTION M1")
		print("  Search Ready")
		for _ in range(13):
			ready = pyautogui.locateOnScreen(f"img/collection/ready{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
			if ready:
				print(f"    Found ready {myUnit} | Search enemy")
				succes = False
				for _ in range(3):
					enemy = pyautogui.locateOnScreen(f"img/collection/enemy{enemyUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
					if enemy:
						print("      Found enemy")
						if moveNumber < 2:
							print("        First Move", end=' | ')
							if useMagic(ready = ready):
								succes = False
								for _ in range(3):
									ready = pyautogui.locateOnScreen(f"img/collection/ready{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
									if ready:
										print("          see ready after Magic | Click enemy")
										click(enemy)
										sleep(2.5)
										if self.logHandler("client -> server: 111 wait for: 0"):
											print("            1st move | hit successfully | sleep 2")
											moveNumber += 1
											succes = True
											sleep(2)
											break
									else:
										print("          Don't see READY AFTER MAGIC")
								if succes:
									if self.moveEnd():
										sleep(4)
										break
								else:
									print("          EXCEPTION C2")
						else:
							print("        Not first Move | Click enemy")
							click(enemy)
							if self.logHandler("client -> server: 111 wait for: 0"):
								print(f"          {moveNumber} move | hit successfully")
								succes = True
								moveNumber += 1
								sleep(2)
								if self.moveEnd():
									sleep(4)
								break
							elif self.logHandler("client -> server: 113 wait for: 0"):
								print(f"          {moveNumber} move | LAST hit successfully")
								succes = True
								moveNumber += 1
								sleep(1)
								break
					else:
						print("      Don't see ENEMY")
				if self.logHandler("server -> client: 114"):
					print("    The battle is completed successfully")
					sleep(2.5)
					self.leftSoft()
					return True
				if not succes:
					print("    EXCEPTION C1")
			else:
				print("  Not found Ready")
				if self.logHandler("server -> client: 114"):
					print("    The battle is completed successfully")
					sleep(2.5)
					self.leftSoft()
					return True
				notReady = pyautogui.locateOnScreen(f"img/collection/notReady{myUnit}.png", minSearchTime=2, region=(450,300,370,350), confidence=.94)
				if notReady:
					print(f"    See notReady {myUnit}| Click")
					click(notReady)
				else:
					print("    Don't see notReady")
				if self.clMessageCheckImage():
					continue

			sleep(1.5)
		print("  EXXXCEPTION COMBAT | MORE THAN 10 MOVES")
	def crossToNextMap(self, x, y):
		print("Try to cross to the next map")
		attempts = 0
		for _ in range(5):
			currentCoors = self.logWalkHandler()
			if currentCoors:
				currentX, currentY = currentCoors[0], currentCoors[1]
				deltaX, deltaY = int(currentX) - x, int(currentY) - y
				print(f"  DeltaX, deltaY - {-deltaX}, {-deltaY}")
				if deltaX < 0:
					press('right', presses = abs(deltaX))
				elif deltaX > 0:
					press('left', presses = deltaX)
				if deltaY < 0:
					press('down', presses = abs(deltaY))
				elif deltaY > 0:
					press('up', presses = deltaY)
				cross = pyautogui.locateOnScreen(f"img/collection/cross.png", minSearchTime=2, region=(0,300,780,724), confidence=.9)
				if cross:
					print("    See cross Button | Click")
					click(cross)
					if self.timeCoorsCheck(x, y, 3):
						print('      The move was successful')
						if self.logHandler('client -> server: 105 wait for: 60'):
							self.send_message('        The cross also was successful', self.token2)
							return True
				else:
					print("    Don't  see crossButtn")
				if self.coordinatesCheck(x, y):
					print('    The move was successful')
					if self.logHandler('client -> server: 105 wait for: 60'):
						print('      The cross also was successful')
						return True
				if self.logHandler("server -> client: 24"):
					print("    Character was attacked by an npc")
					if self.searchBattle():
						if self.combat():
							continue
				if self.clMessageCheckImage():
					self.toCenter()
					continue
				self.startMove()
			else:
				print("  Can't get current coordinates")
			self.toCenter()
			attempts += 1
			print(f"  Attempt {attempts} COMPLETED")
		self.send_message("    CROSS FAILED | FALSE", self.token2)
		return False
	def goInGate(self, x, y):
		self.send_message("Enter the gate", self.token2)
		attempts = 0
		for i in range(3):
			if i > 0:
				self.startMove()
			currentCoors = self.logWalkHandler()
			if currentCoors:
				currentX, currentY = currentCoors[0], currentCoors[1]
				deltaX, deltaY = int(currentX) - x, int(currentY) - y
				print(f"  DeltaX, deltaY - {-deltaX}, {-deltaY}")
				if deltaX < 0:
					press('right', presses = abs(deltaX))
				elif deltaX > 0:
					press('left', presses = deltaX)
				if deltaY < 0:
					press('down', presses = abs(deltaY))
				elif deltaY > 0:
					press('up', presses = deltaY)
				self.leftSoft()
				lsEnterTheGate = pyautogui.locateCenterOnScreen("img/collection/lsEnterTheGate.png", minSearchTime=2, region=(0, 500, 700, 524), confidence=.92)
				if lsEnterTheGate:
					print("    See EnterTheGate Button | Click")
					click(lsEnterTheGate)
					sleep(1.5)
					if self.logHandler("client -> server: 1012 wait for: 72"):
						self.send_message('      Enter The Gate was successful', self.token2)
						return True
				else:
					print("    Don't  see EnterTheGate")
				if self.clMessageCheckImage():
					self.toCenter()
					continue
			else:
				print("  Can't get current coordinates")
			self.toCenter()
			attempts += 1
			print(f"  Attempt {attempts} COMPLETED")
		self.send_message("    ENTER THE GATE FAILED | FALSE", self.token2)
		return False
	def chooseLand(self, land):
		self.send_message("Choose the land in the gate", self.token2)
		attempts = 0
		for i in range(3):
			landSellect = pyautogui.locateCenterOnScreen("img/collection/landSellect.png", minSearchTime=2, region=(0, 0, 1000, 524), confidence=.92)
			if landSellect:
				print("  See 'Land Sellect' | Click")
				click(landSellect)
				sleep(.2)
			else:
				print("  Don't SEE 'LAND SELECT'")
			wishLand = pyautogui.locateCenterOnScreen(f"img/collection/land{land}.png", minSearchTime=2, region=(0, 0, 1000, 1024), confidence=.92)
			if wishLand:
				print(f"  See {land} | Click")
				click(wishLand)
				sleep(.5)
				self.leftSoft()
			else:
				print(f"  DON'T SEE {land}")
			if self.logHandler("client -> server: 106 wait for: 1012"):
				self.send_message(f'    Teleportation to {land} was successful', self.token2)
				# leftSoft()
				return True
			if self.clMessageCheckImage():
				self.toCenter()
				continue
			attempts += 1
			print(f"  Attempt {attempts} COMPLETED")
		self.send_message("    TELEPORTATION FAILED | FALSE", self.token2)
		self.rightSoft()
		return False
	def farmingGold(self, unit = "Camel", magic = False, magnetAngle = "1", region=(0, 0, 1200, 1200), camel = False):
		print("Run Farm method")
		for _ in range(3):
			sb = self.searchBotFarm(enemy = unit, side = magnetAngle, region = region)
			if sb == 'NICE':
				for _ in range(3):    
					if self.logHandler("client -> server: 109 wait for: 24"):
						print(f"  {unit} attack Successful")
						sleep(.5)
						for _ in range(3):
							if self.logHandler("server -> client: 109", stop = True):
								print("    The npc joins or was killed")
								for _ in range(3):
									print("      Don't see peace agreement")
									battleImpossible = pyautogui.locateOnScreen("img/collection/battleImpossible.png", minSearchTime=2, region=(100, 0, 800, 300), confidence=.95, grayscale = True)
									if battleImpossible:
										print("        Battle Impossible | Click LSoft")
										self.leftSoft()
										return "KILLED"
									else:
										print("        Don't see 'Battle Impossible'")
										print("        EXCEPTION col6")
								print("    EXCEPTION col3")
							elif self.logHandler("server -> client: 24"):
								print("    Combat found")
								if self.searchBattle():
									if camel:
										if self.combatCamel():
											return "Battle"
										else:
											return "FailedBattle"										
									else:
										if unit == "Camel":
											if magic:
												if self.combatMix():
													return "Battle"
												else:
													return "FailedBattle"
											else:
												if self.combatSimple():
													return "Battle"
												else:
													return "FailedBattle"
										elif unit == "Dragon":
											if self.combatSimple():
												return "Battle"
											else:
												return "FailedBattle"
						print("  EXCEPTION col2")
					sleep(1)
				print("  EXCEPTION col1")
			elif sb == 'NOCLICK':
				continue
			elif self.logHandler("server -> client: 24"):
				print("  Character was attacked by an npc")
				if self.searchBattle():
					if unit == "Camel":
						if magic:
							if self.combatMix():
								return "Battle"
							else:
								return "FailedBattle"
						else:
							if self.combatSimple():
								return "Battle"
							else:
								return "FailedBattle"
					elif unit == "Dragon":
						if self.combatSimple():
							return "Battle"
						else:
							return "FailedBattle"
			if unit == "Camel":
				if self.clMessageCheckImage():
					continue
			if sb == 'NOBOTS':
				return "NOBOTS"
		print("GOLD FARM METHOD FAILED")
		return "FAILED"
	def collectArmy(self, unit = "Dragon"):
		self.send_message("Collecting an army", self.token2)
		for _ in range(3):
			sb = self.searchBot(enemy = unit)
			if sb == 'NICE':
				for _ in range(3):    
					if self.logHandler("client -> server: 109 wait for: 24"):
						print("  Dragon attack Successful")
						sleep(.5)
						for _ in range(3):
							if self.logHandler("server -> client: 109", stop = True):
								print("    The npc joins or was killed")
								for _ in range(3):
									peaceAgreement = pyautogui.locateOnScreen("img/collection/peaceAgreement.png", minSearchTime=2, region=(0, 0, 1000, 300), confidence=.95, grayscale = True)
									if peaceAgreement:
										print("      The npc joins | Click Yes")
										self.leftSoft()
										for _ in range(3):
											sleep(1)
											if self.logHandler("client -> server: 109 wait for: 20"):
												for _ in range(3):
													sleep(1)
													if self.logHandler("server -> client: 141"):
														self.send_message(f"        The {self.joinedBots + 1} npc was successfully joined", self.token2)
														self.joinedBots += 1
														return "JOINED"
												print("      EXCEPTION col5")
										print("      EXCEPTION col4")
									else:
										print("      Don't see peace agreement")
										battleImpossible = pyautogui.locateOnScreen("img/collection/battleImpossible.png", minSearchTime=2, region=(100, 0, 800, 300), confidence=.95, grayscale = True)
										if battleImpossible:
											print("        Battle Impossible | Click LSoft")
											self.leftSoft()
											return "KILLED"
										else:
											print("        Don't see 'Battle Impossible'")
											print("        EXCEPTION col6")
								print("    EXCEPTION col3")
							elif self.logHandler("server -> client: 24"):
								print("    Combat found")
								if self.searchBattle():
									if self.combat():
										return True
						print("  EXCEPTION col2")
					sleep(1)
				print("  EXCEPTION col1")
			elif sb == 'NOCLICK':
				continue
			elif self.logHandler("server -> client: 24"):
				print("  Character was attacked by an npc")
				if self.searchBattle():
					if self.combat():
						return True
			elif sb == 'NOBOTS':
				break
	def collectLast(self):
		self.send_message("Collect Last Bot", self.token2)
		for _ in range(3):
			sb = self.searchBot(coorsMatch = False)
			if sb == 'NICE':
				for _ in range(3):    
					if self.logHandler("client -> server: 109 wait for: 24"):
						print("  Dragon attack Successful")
						sleep(.5)
						for _ in range(3):
							if self.logHandler("server -> client: 109", stop = True):
								print("    The npc joins or was killed")
								for _ in range(3):
									peaceAgreement = pyautogui.locateOnScreen("img/collection/peaceAgreement.png", minSearchTime=2, region=(0, 0, 1000, 300), confidence=.95, grayscale = True)
									if peaceAgreement:
										print("      The npc joins | Click Yes")
										self.leftSoft()
										for _ in range(3):
											sleep(1)
											if self.logHandler("client -> server: 109 wait for: 20"):
												for _ in range(3):
													sleep(1)
													if self.logHandler("server -> client: 141"):
														self.send_message("        The npc was successfully joined", self.token2)
														joinedLast += 1
														return "JOINED"
												print("        EXCEPTION col5")
										print("      EXCEPTION col4")
									else:
										print("      Don't see peace agreement")
										print("      Npc has not joined")
										battleImpossible = pyautogui.locateOnScreen("img/collection/battleImpossible.png", minSearchTime=2, region=(100, 0, 800, 300), confidence=.95, grayscale = True)
										if battleImpossible:
											self.send_message("Battle Impossible | Click LSoft", self.token2)
											self.leftSoft()
											return "KILLED"
										else:
											print("      Don't see 'Battle Impossible'")
											print("      EXCEPTION col6")
								print("    EXCEPTION col3")
							elif self.logHandler("server -> client: 24"):
								self.send_message("Combat found", self.token2)
								if self.searchBattle():
									if self.combatExtented(magicSpell = "PowerOfDeath"):
										return "COMBAT"
						print("    EXCEPTION col2")
					sleep(1)
				print("  EXCEPTION col1")
			elif sb == 'NOCLICK':
				return "KILLED"
			elif self.logHandler("server -> client: 24"):
				self.send_message("  Character was attacked by an npc", self.token2)
				if self.searchBattle():
					if self.combatExtented(magicSpell = "PowerOfDeath"):
						return True
			elif sb == 'NOBOTS':
				return "NOBOTS"
	def collectSpider(self):
		self.send_message("Collect Spider", self.token2)
		for _ in range(3):
			sb = self.searchBot(enemy = "Spider", coorsMatch = False)
			if sb == 'NICE':
				for _ in range(3):    
					if self.logHandler("client -> server: 109 wait for: 24"):
						print("  Spider attack Successful")
						sleep(.5)
						for _ in range(3):
							if self.logHandler("server -> client: 109", stop = True):
								print("    The npc joins or was killed")
								for _ in range(3):
									peaceAgreement = pyautogui.locateOnScreen("img/collection/peaceAgreement.png", minSearchTime=2, region=(0, 0, 1000, 300), confidence=.95, grayscale = True)
									if peaceAgreement:
										print("      The npc joins | Click Yes")
										self.leftSoft()
										for _ in range(3):
											sleep(1)
											if self.logHandler("client -> server: 109 wait for: 20"):
												for _ in range(3):
													sleep(1)
													if self.logHandler("server -> client: 141"):
														self.send_message("        The npc was successfully joined", self.token2)
														return "JOINED"
												print("        EXCEPTION col5")
										print("      EXCEPTION col4")
									else:
										print("      Don't see peace agreement")
										battleImpossible = pyautogui.locateOnScreen("img/collection/battleImpossible.png", minSearchTime=2, region=(100, 0, 800, 300), confidence=.95, grayscale = True)
										if battleImpossible:
											self.send_message("        Battle Impossible | Click LSoft")
											self.leftSoft()
											return "KILLED"
										else:
											print("        Don't see 'Battle Impossible'")
											print("        EXCEPTION col6")
								print("    EXCEPTION col3")
							elif self.logHandler("server -> client: 24"):
								self.send_message("    Combat found", self.token2)
								if self.searchBattle():
									if self.combatExtented(myUnit = "Dragon", enemyUnit = "Spider", magicSpell = "BlindingLight"):
										return "COMBAT"
						print("  EXCEPTION col2")
					sleep(1)
				print("  EXCEPTION col1")
			elif sb == 'NOCLICK':
				continue
			elif sb == 'NOBOTS':
				return "NOBOTS"
			elif self.logHandler("server -> client: 24"):
				self.send_message("  Character was attacked by an npc", self.token2)
				if self.searchBattle():
					if self.combatExtented(myUnit = "Dragon", enemyUnit = "Spider", magicSpell = "BlindingLight"):
						return True
	def zeroExp(self, keyPhrase = "img=header_bg.png"):
		print(f"ZERO CHECK. LS the log file | Start with {self.endingIndex}")
		with open(log_file_path, 'r') as file:
			file = file.read()
		position = file.rfind(keyPhrase)
		if position != -1:
			print(f'  LOG 1 SUCCES {keyPhrase} found on position {position}')
			expPosition = file.find("Заработано опыта: ", position)
			if expPosition != -1:
				print(f'    LOG 2 SUCCES | experience found on position {expPosition}')
				experience = file[expPosition + 18 : expPosition + 18 + 2]
				print(f"    Experience is {experience}")
				if experience.strip() == '0':
					resExpPosition = file.find("Зарезервировано опыта: ", expPosition)
					if resExpPosition != -1:
						print(f'      LOG 3 SUCCES | experience found on position {resExpPosition}')
						resExperience = file[resExpPosition + 21 : resExpPosition + 23]
						print(f"       Reserve experience is {resExperience}")
						if resExperience.strip() == '0':
							print(f"        Zero check is successful. ZERO")
							return True
						else:
							print(f"        Zero check is successful. NOT ZERO")
							return False
					else:
						print("        Don't see reserve experience. Completed")
						return True
				else:
					print(f"      Zero check is successful. NOT ZERO")
					return False
			else:
				print(f"    Can't find Experience")
				return False
		else:
			print(f'  log FAILED {keyPhrase} not found within range [{self.endingIndex} - end]')
			return False
	def followTheRoute(self, route, unit = "Dragon", collect = False, disband = False, maxJoin = 9, exactCoors = (-1, -1)):
		self.send_message("Move along the route", self.token2)
		point = 0
		if exactCoors[0] == 0 and exactCoors[1] == 0:
			deltaX, deltaY = 0, 0    
		else:
			deltaX, deltaY = random.randint(-1, 1), random.randint(-1, 1)
		print(f"  Delta X, Delta Y - {deltaX}, {deltaY}")
		for coors in route:
			if coors[0] == exactCoors[0] and coors[1] == exactCoors[1]:
				print("    EXACT COORS MATCH")
				if deltaX != 0:
					print(f"      DeltaX = {deltaX} | DeltaY is 0")
					deltaY = 0
			if self.joinedBots >= maxJoin:
				print(f"    {self.joinedBots} have already joined | Need {maxJoin}")
				collect = False
			if not self.moveOnMap(coors[0] + deltaX, coors[1] + deltaY):
				print(f"    Can't move in coordinates {coors[0] + deltaX} {coors[1] + deltaY}")
				self.send_message("    Route completion FAILED | FALSE", self.token2)
				return False
			else:
				point += 1
				print(f"    Point {point} ({coors[0]}:{coors[1]}) has been reached")
				if collect:
					for k in range(3):
						if self.joinedBots < maxJoin:
							self.collectArmy()
						if disband:
							if self.joinedBots == 2 and not self.dissed:
								if self.disbandOneUnit(unit):
									self.dissed = True
								self.outOfCharacterMap()
						if self.botListLenght < 2:
							print(f"      Bot list lenght is {self.botListLenght} | break")
							break
					self.moveOnMap(coors[0] + deltaX, coors[1] + deltaY)
		self.send_message("  Route completion Successful", self.token2)
		return True
	def followTheRoutePumpkin(self, route, unit = "Dragon", collect = False, exactCoors = (-1, -1), side = "2", zero = False, bats = True, magic = False):
		self.send_message("Move along the route", self.token2)
		point = 0
		if exactCoors[0] == 0 and exactCoors[1] == 0:
			deltaX, deltaY = 0, 0    
		else:
			deltaX, deltaY = random.randint(-1, 1), random.randint(-1, 1)
		print(f"  Delta X, Delta Y - {deltaX}, {deltaY}")
		for coors in route:
			if coors[0] == exactCoors[0] and coors[1] == exactCoors[1]:
				print("    EXACT COORS MATCH")
				if deltaX != 0:
					print(f"      DeltaX = {deltaX} | DeltaY is 0")
					deltaY = 0
			if not self.moveOnMap(coors[0] + deltaX, coors[1] + deltaY, npcAttack = False):
				print(f"    Can't move in coordinates {coors[0] + deltaX} {coors[1] + deltaY}")
				self.send_message("    Route completion FAILED | FALSE", self.token2)
				return False
			else:
				point += 1
				print(f"    Point {point} ({coors[0]}:{coors[1]}) has been reached")
				if zero:
					if self.battleNumber > 0 and self.battleNumber % 3 == 0:
						if self.zeroExp():
							return False
				if collect:
					for k in range(2):
						if bats and k > 0:
							break
						fg = self.farmingGold(unit = unit, magic = magic, magnetAngle = side)
						if fg == "NOBOTS":
							if not bats:
								break
						elif fg == "FailedBattle":
							return False
						elif fg == "Battle" or fg == "KILLED":
							if self.npcCount == 1:
								print("    Only 1 NPC. break")
								break
						else:
							if bats:
								if not self.moveOnMap(coors[0] + deltaX, coors[1] + deltaY, npcAttack = False):
									print(f"    Can't move in coordinates {coors[0] + deltaX} {coors[1] + deltaY}")
									self.send_message("    Route completion FAILED | FALSE", self.token2)
									return False
		self.send_message("  Route completion Successful", self.token2)
		return True
	def followTheRouteBats(self, route, unit = "Dragon", collect = False, exactCoors = (-1, -1), side = "2", zero = False, bats = True):
		self.send_message("Move along the route (Bats)", self.token2)
		point = 0
		for coors in route:
			if exactCoors[0] == 0 and exactCoors[1] == 0:
				deltaX, deltaY = 0, 0    
			else:
				deltaX, deltaY = random.randint(-1, 1), random.randint(-1, 1)
			print(f"  Delta X, Delta Y - {deltaX}, {deltaY}")
			if coors[0] == exactCoors[0] and coors[1] == exactCoors[1]:
				print("    EXACT COORS MATCH")
				if deltaX != 0:
					print(f"      DeltaX = {deltaX} | DeltaY is 0")
					deltaY = 0
			if not self.moveOnMap(coors[0] + deltaX, coors[1] + deltaY, npcAttack = False):
				print(f"    Can't move in coordinates {coors[0] + deltaX} {coors[1] + deltaY}")
				self.send_message("    Route completion FAILED | FALSE", self.token2)
				return False
			else:
				point += 1
				print(f"    Point {point} ({coors[0]}:{coors[1]}) has been reached")
				if zero:
					if self.battleNumber > 0 and self.battleNumber % 3 == 0:
						if self.zeroExp():
							return False
				if collect:
					for k in range(2):
						if coors[2] == 'noFarm':
							break
						fg = self.farmingGold(unit = unit, magic = False, magnetAngle = side, region=coors[2])
						if fg == "NOBOTS":
							if not bats:
								break
						elif fg == "Battle":
							break
						elif fg == "KILLED":
							if self.npcCount == 1:
								print("    Only 1 NPC. break")
								break
						elif fg == "FailedBattle":
							return False
						else:
							if bats:
								if exactCoors[0] == 0 and exactCoors[1] == 0:
									deltaX, deltaY = 0, 0    
								else:
									deltaX, deltaY = random.randint(-1, 1), random.randint(-1, 1)
								if coors[0] == exactCoors[0] and coors[1] == exactCoors[1]:
									print("    EXACT COORS MATCH")
									if deltaX != 0:
										print(f"      DeltaX = {deltaX} | DeltaY is 0")
										deltaY = 0
								if not self.moveOnMap(coors[0] + deltaX, coors[1] + deltaY, npcAttack = False):
									print(f"    Can't move in coordinates {coors[0] + deltaX} {coors[1] + deltaY}")
									self.send_message("    Route completion FAILED | FALSE", self.token2)
									return False
		self.send_message("  Route completion Successful", self.token2)
		return True
	def orderTeleport(self, town):
		print("Order Teleport Run")
		def openList():
			print("Open Town List")
			for _ in range(3):
				self.leftSoft()
				townList =  pyautogui.locateOnScreen(f"img/collection/townList.png", minSearchTime=2, region=(0,0,780,1024), confidence=.92)
				if townList:
					print("  See Town List | Click ")
					click(townList)
					sleep(1)
					if self.logHandler("client -> server: 167 wait for: 153"):
						print("    City list opened Succes")
						return True
				else:
					print("  DON'T SEE TOWN LIST")
					self.toCenter()
			self.send_message("    TOWN LIST OPEN FAILED | FALSE", self.token2)
			return False
		def teleport():
			print("Use Teleport")
			for _ in range(3):
				clTown = pyautogui.locateOnScreen(f"img/collection/cl{town}.png", minSearchTime=2, region=(0,0,1280,1024), confidence=.92)
				if clTown:
					print(f"  See {town} | Click ")
					click(clTown)
					sleep(1)
				else:
					print(f"  DON'T SEE {town}")
					self.rightSoft()
					return "False"
				if self.logHandler("client -> server: 168 wait for: 1012"):
					self.send_message("    Using Teleport Succes", self.token2)
					return "True"
			self.send_message("     Use TELEPORT FAILED | FALSE", self.token2)
			self.rightSoft()
			return False
		for _ in range(2):
			if openList():
				tp = teleport()
				if tp == "True":
					if self.defineTheCity() == town:
						return True
				elif tp == "False":
					self.send_message(f"    city {town} miss", self.token2)
					return False
		print("  TELEPORTATION FAILED | FALSE")
		return False
	def orderTpMulti(self, cityList):
		foundCity = "KKKKKK"
		print("Use Order Teleport Multi")
		def openList():
			print("Open Town List")
			for _ in range(3):
				self.leftSoft()
				townList =  pyautogui.locateOnScreen(f"img/collection/townList.png", minSearchTime=2, region=(0,0,780,1024), confidence=.92)
				if townList:
					print("  See Town List | Click ")
					click(townList)
					sleep(1)
					if self.logHandler("client -> server: 167 wait for: 153"):
						print("    City list opened Succes")
						return True
				else:
					print("  DON'T SEE TOWN LIST")
					self.toCenter()
			self.send_message("    TOWN LIST OPEN FAILED | FALSE", self.token2)
			return False
		def teleport():
			nonlocal foundCity
			print("Use Teleport")
			for city in cityList:
				clTown = pyautogui.locateOnScreen(f"img/collection/cl{city}.png", minSearchTime=2, region=(0,0,1280,1024), confidence=.92)
				if clTown:
					print(f"  See {city} ")
					click(clTown)
					sleep(1)
					foundCity = city
					if self.logHandler("client -> server: 168 wait for: 1012"):
						self.send_message("    Using Teleport Succes", self.token2)
						return "True"
				else:
					print(f"  DON'T SEE {city}")
			if self.logHandler("client -> server: 168 wait for: 1012"):
				self.send_message("    Using Teleport Succes", self.token2)
				return "True"
			print("  TELEPORT FAILED | FALSE")
			self.rightSoft()
			return False

		for _ in range(2):
			if openList():
				tp = teleport()
				if tp == "True":
					if self.defineTheCity() == foundCity:
						return foundCity
		print("  TELEPORTATION FAILED | FALSE")
		return False
	def bagFullness(self, bagSize = 30):
		def econonyOpen():
			print("Open the economy")
			for _ in range(3):
				self.leftSoft()
				economy = pyautogui.locateOnScreen(f"img/collection/lsEconomy.png", minSearchTime=2, region=(0,0,780,1024), confidence=.93)
				if economy:
					print("  See economyButton | Click")
					click(economy)
				else:
					print("  Don't see economyButton")
				sleep(.5)
				if self.logHandler("client -> server: 145 wait for: 145"):
					return True
				economyMenu = pyautogui.locateOnScreen(f"img/collection/characterMenu.png", minSearchTime=2, region=(450,0,450,324), confidence=.9)
				if economyMenu:
					print("  See the economy menu")
					return True
				else:
					print("  Don't see economy menu")
				if self.clMessageCheckImage():
					continue
			print("    Economy open Failed | FALSE")
			return False
		def logFullnessHandler(fullBag = bagSize, keyPhrase = "Заполненность сумки: "):
			print(f"LS the log file | Start with {self.endingIndex}")
			for _ in range(3):
				with open(log_file_path, 'r') as file:
					file = file.read()
				position = file.rfind(keyPhrase, self.endingIndex)
				if position != -1:
					print(f'  LOG 1 SUCCES {keyPhrase} found on position {position}')
					fullness = file[position + len(keyPhrase) : position + len(keyPhrase) + 2]
					print(f"    Fullness is {fullness}")
					if int(fullness) >= fullBag:
						print(f"      The bag is overflowing | Log check is successful")
						return "FULL"
					else:
						print(f"      Bag is not full - {fullness}")
						return "NOTFULL"
				else:
					print(f'  log FAILED {keyPhrase} not found within range [{self.endingIndex} - end]')
					sleep(1)
			return "NOTFOUND"
		if econonyOpen():
			lFH = logFullnessHandler()
			if lFH == 'FULL':
				return 'FULL'
			elif lFH == 'NOTFULL':
				return 'NOTFULL' 
			elif lFH == "NOTFOUND":
				return 'FALSE' 
		else:
			return "FALSE"
	def emptyBackpack(self, bagSize = 30, magicInTheBag = False):
		def gotoMarkt():
			print("Trying to open the Markt")
			for _ in range(3):
				markt = pyautogui.locateOnScreen(f"img/collection/townMarkt.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
				if markt:
					print("  See Markt | Click | Search shop")
					click(markt)
				if self.logHandler("client -> server: 72 wait for: 74"):
					print("  Right LOG | Markt Succes")
					return True
				shop = pyautogui.locateOnScreen(f"img/collection/townShop.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
				if shop:
					print("  See Shop | Markt Succes")
					return True
				if self.clMessageCheckImage():
					continue
			print("Can't open Markt | FALSE")
			return False
		def gotoShop():
			print("Trying to open the shop")
			for _ in range(3):
				shop = pyautogui.locateOnScreen(f"img/collection/townShop.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
				if shop:
					print("  See Shhop | Click | Search inside shop")
					click(shop)
				if self.logHandler("client -> server: 216 wait for: 153"):
					print("  Right LOG | Shop Succes")
					return True
				inside = pyautogui.locateOnScreen(f"img/collection/insideShop.png", minSearchTime=2, region=(600,0,680,524), confidence=.9)
				if inside:
					print("  See insideShop | Shop Succes")
					return True
				if self.clMessageCheckImage():
					continue
			print("    Can't open Shop | FALSE")
			return False
		def sellAll():
			if magicInTheBag:
				press('right')
			sleep(.2)
			for _ in range(bagSize + 5):
				press(['enter', 'right', 'enter', 'right'])
			press('enter')
			for _ in range(3):
				self.rightSoft()
				deal = pyautogui.locateOnScreen(f"img/collection/rsDeal.png", minSearchTime=2, region=(500,0,780,1024), confidence=.9)
				if deal:
					print("  See Deal | Click | Deal")
					click(deal)
					sleep(2.5)
				else:
					print("  Don't see Deal button")
				if self.logHandler("client -> server: 101 wait for: 25"):
					print("  Right LOG | Deal Succes")
					return True
				shop = pyautogui.locateOnScreen(f"img/collection/townShop.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
				if shop:
					print("  See fromShop | Enter complete")
					return True
				else:
					print("  Don't see fromShop")
				if self.clMessageCheckImage():
					continue
		def exit():
			print("Trying to leave Bastion")
			for _ in range(5):
				shop = pyautogui.locateOnScreen(f"img/collection/townShop.png", minSearchTime=2, region=(0,0,1280,524), confidence=.9)
				if shop:
					print("See fromShop | Leave Markt")
					self.rightSoft()
				print("Search inTheCity")
				inTheCity = pyautogui.locateOnScreen(f"img/collection/inTheCity.png", minSearchTime=2, region=(0,0,1280, 1024), confidence=.85)
				if inTheCity:
					print("The character is in the city")
					return True
				else:
					print("Don't see inTheCity")
				if self.clMessageCheckImage():
					continue
			print("  Can't buy. Exit from bastion | FALSE")
			return False
		attempt = 0
		while attempt <= 3:
			if self.checkInTheCity():
				print("Found in City")
			else:
				self.relogin()
				attempt += 1
				continue
			if gotoMarkt():
				if gotoShop():
					if sellAll():
						if exit():
							return True
						else:
							print("EXIT FAILED")
							self.relogin()
							attempt += 1
							continue
					else:
						print("SELL FAILED")
						self.relogin()
						attempt += 1
						continue
				else:
					print("SHOP FAILED")
					self.relogin()
					attempt += 1
					continue
			else:
				print("MARKT FAILED")
				self.relogin()
				attempt += 1
				continue
	def replaceCamel(self, noCamel = True):
		try:
			client, folder = data["images"][self.race], "Camel"
			if noCamel:
				folder = "noCamel"
			result = subprocess.Popen(["7z", "a", f"/home/{self.username}/Desktop/gnomLinux/Clients/{client}.jar", f"./img/{folder}/*"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			output, errors = result.communicate()
			print("Output: ", output.decode("utf-8"))
			print("Errors: ", errors.decode("utf-8"))
		except FileNotFoundError:
			print("File not found")
		except Exception as e:
			print("Another error: ", e)