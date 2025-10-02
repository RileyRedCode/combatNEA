import pygame, json, math, MapGen, random

WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
TILE_SIZE = 40
SCREEN_SIZE = (800,800)
TERRAIN_SIZE = (800, 800)
MAP_WIDTH = 20
MAP_RES = (TERRAIN_SIZE[0]*MAP_WIDTH, TERRAIN_SIZE[1]*MAP_WIDTH)

'''
Name: checkCollision
Parameters: x1:int, x2:int, y1:int, y2:int, ox1:int, ox2:int, oy1:int, oy2:int
Returns: boolean
Purpose: Returns True or false depending on if the two rectangles given overlap.
'''
def checkCollision(x1, x2, y1, y2, ox1, ox2, oy1, oy2):#Give the start and end points of each objects x and y axis
	if ((x1 <= ox1 < x2) or (x1 < ox2 <= x2) or (ox1 < x1 < ox2)) and ((y1 <= oy1 < y2) or (y1 < oy2 <= y2) or (oy1 < y1 < oy2)):
		return True
	else:
		return False

'''
Name: Node
Purpose: These are invisible points which are scattered around the map in a grid 
format. They are used for pathfinding and lay out where an enemy can and can't travel to.
'''
class Node:

	'''
	Name: __init__
	Parameters: x:integer, y:integer
	Returns: None
	Purpose: Constructor for Nodes.
	'''
	def __init__(self, x, y):
		self.mapX, self.mapY = x, y
		self.up = False
		self.down = False
		self.left = False
		self.right = False
		self.topLeft = False
		self.topRight = False
		self.bottomRight = False
		self.bottomLeft = False
		self.neighbours = []

	'''
	Name: __repr__
	Parameters: None
	Returns: f"{self.mapX},{self.mapY}":string
	Purpose: This returns a string containing the position the node is located at.
	It is used for debugging purposes.
	'''
	def __repr__(self):
		return f"[{self.mapX},{self.mapY}]"

'''
Name: World
Purpose: Used to store all world related variables such as nodes, obstacles, and structures. 
It is also used for establishing Nodes.
'''
class World:

	'''
	Name: __init__
	Parameters: textMap:list, obstacles:spriteGroup
	Returns: None
	Purpose: Constructor
	'''
	def __init__(self, textMap, obstacles):
		self.x = 0
		self.y = 0
		mapGen = MapGen.MapGenerator(textMap, obstacles)
		self.img, self.obstacleList = mapGen. finalise()
		# Convert the PIL Image to a pygame Surface so that it can blit-ed without any issues
		img_bytes = self.img.tobytes()
		img_size = self.img.size
		img_mode = self.img.mode
		self.img = pygame.image.fromstring(img_bytes, img_size, img_mode)#fromstring requires the bytes for the image, the size and the mode
		self.tileMap = mapGen.textMap
		self.worldSurface = pygame.Surface((MAP_RES))
		self.worldSurface.blit(self.img, (0, 0))
		self.nodes = [[False for count in range(MAP_WIDTH*(SCREEN_SIZE[1]//TILE_SIZE))] for i in range(MAP_WIDTH*(SCREEN_SIZE[0]//TILE_SIZE))]#Establishes a plain grid

	'''
	Name: draw
	Parameters: screen:rect
	Returns: None
	Purpose: draws the map onto the screen
	'''
	def draw(self, screen):
		screen.blit(self.worldSurface, (self.x, self.y))

'''
Name: Hud
Purpose: This is a heads up display which displays information like Health to the player.
'''
class Hud:

	'''
	Name: __init__
	Parameters: owner:object
	Returns: None
	Purpose: Initializes the hud.
	'''
	def __init__(self, owner):
		self.owner = owner
		self.animation = False#This indicates when an animation is playing
		#Health bar section
		self.displayHealth = 100
		self.displayDamage = 0
		self.displayHeal = 0
		# dimensions are 110 by 30
		self.healthbar = pygame.image.load("Assets/healthbar.png")
		self.healthbar = pygame.transform.scale(self.healthbar,(220, 60))

		#colours
		self.healthBgColour = (25, 25, 25)
		self.white = (255, 255, 255)
		self.healthColour = (255, 120, 90)
		self.green = (0, 200, 30)

		self.health = pygame.surface.Surface((self.displayHealth, 40))
		self.health.fill(self.healthColour)
		self.damage = pygame.surface.Surface((self.displayHealth, 40))
		self.damage.fill(self.white)
		self.heal = pygame.surface.Surface((1, 40))
		self.heal.fill(self.green)
		self.background = pygame.surface.Surface((self.displayHealth*2, 40))
		self.background.fill(self.healthBgColour)

		self.revive = pygame.image.load("Assets/revive.png")
		self.revive = pygame.transform.scale(self.revive, (60, 60))
		self.reviveRect = self.revive.get_rect()
		self.reviveRect.center = (400, 650)

		#Talking
		self.talkBg = pygame.image.load("Assets/talkBg.png")
		self.talkBgRect = self.talkBg.get_rect()
		self.talkBgRect.center = (900, 400)

		self.textbox = pygame.Surface((800, 250), pygame.SRCALPHA)
		self.textbox.fill((0, 0, 0, 150))
		self.textboxRect = self.textbox.get_rect()
		self.textboxRect.bottomright = (0, 800)

		self.textDone = False
		self.jitter = False
		self.letters = 0
		self.letterStart = 0
		self.chatNumber = 0
		self.optionSelect = 0
		self.chatPos = False
		self.cooldown = False
		self.font = pygame.font.SysFont('Times New Roman', 40)

		self.message = "My name is EDWIN, I made the mimic."
		self.text = self.font.render((""), False, (255, 255, 255))
		self.textList = []

		self.continueTxt = self.font.render(("Press space to continue"), False, (255, 255, 255))
		self.continueDis = False
		self.optionDis = False

		#Menu
		self.menuBg = pygame.Surface((800, 800), pygame.SRCALPHA)
		self.menuBg.fill((0, 0, 0, 150))
		self.menuBgRect = self.menuBg.get_rect()
		self.menuBgRect.topleft = (0, 800)

		self.menuPos = 0
		self.menuOptions = ["Resume", "Items", "Controls"]
		self.menuTxt = []
		for op in self.menuOptions:
			self.menuTxt.append(self.font.render(op, False, (255, 255, 255)))
		self.menuActivity = False

		self.inventoryPos = 0
		self.inventoryOptions = []
		self.inventoryText = []
		self.details = []
		self.startTime = pygame.time.get_ticks()
		self.escapeText = self.font.render("Press escape to go back to menu", False, (255, 255, 255))
		self.controlText = []

	'''
	Name: draw
	Parameters: screen:rect
	Returns: None
	Purpose: Displays the Hud
	'''
	def draw(self, screen):
		screen.blit(self.background, (TILE_SIZE // 4 + 10, TILE_SIZE // 4 + 10))
		screen.blit(self.damage,((TILE_SIZE//4) + 10 + (self.displayHealth * 2) - 1, TILE_SIZE//4 + 10))
		screen.blit(self.heal, ((TILE_SIZE // 4) + 10 + (self.displayHealth * 2) - 1, TILE_SIZE // 4 + 10))
		screen.blit(self.health,(TILE_SIZE//4 + 10 - 1, TILE_SIZE//4 + 10))
		screen.blit(self.healthbar, (TILE_SIZE//4, TILE_SIZE//4))

		if self.owner.talking:
			#Layoutss
			screen.blit(self.talkBg, self.talkBgRect)
			screen.blit(self.speaker, self.speakerRect)
			screen.blit(self.textbox, self.textboxRect)
			#Text
			if not self.animation:
				#Dialogue
				x,y = 10, 560
				for text in self.textList:
					screen.blit(text, (x, y))
					y += 45
				screen.blit(self.text, (x, y))
				#Continue options
				if self.continueDis:
					screen.blit(self.continueTxt, (420, 755))
				elif self.optionDis:
					x, y = 600, 560
					for option in self.optionDis:
						screen.blit(option, (x, y))
						y += 45
		if self.owner.paused or self.animation == "menuC":
			screen.blit(self.menuBg, self.menuBgRect)
			if not self.animation:
				if not self.menuActivity:
					x,y = 300, 200
					for text in self.menuTxt:
						screen.blit(text, (x, y))
						y += 60

				if self.menuActivity == "Items":
					x, y = 20, 40
					for text in self.inventoryText:
						screen.blit(text, (x, y))
						y += 50
					x, y = 200, 460
					for text in self.details[0]:
						screen.blit(text, (x, y))
						y += 60
					screen.blit(self.weaponImage, self.weaponRect)
					screen.blit(self.details[1], (600,400))
					screen.blit(self.details[2], (200, 400))
					screen.blit(self.escapeText, (200, 730))

				if self.menuActivity == "Controls":
					x, y = 100, 200
					for control in self.controlText:
						screen.blit(control, (x, y))
						y += 60
					screen.blit(self.escapeText, (200, 730))

		if self.owner.revive:
			screen.blit(self.revive, self.reviveRect)

	'''
	Name: startAnimation
	Parameters: type:string, npc:object
	Returns: None
	Purpose: This is used to manage starting animations and any processes that need to be completed first.
	'''
	def startAnimation(self, type, npc = False):
		if type == "open":
			self.jitter = False
			self.animation = "open"
			self.speaker, self.dialogue, self.chatPos = npc.getSpeaker()
			self.speakerRect = self.speaker.get_rect()
			self.textboxRect.bottomright = (0, 800)
			self.speakerRect.center = 860, 400
			self.talkBgRect.center = (900, 400)
			for node in self.dialogue.nodes:
				if node.name == self.chatPos:
					self.chatPos = node
					self.chatNumber = random.randint(0, len(self.chatPos.neighbours)-1)
		elif type == "close":
			self.animation = "close"

		elif type == "menu":
			self.menuBgRect.topleft = (0, 800)
			self.animation = "menuO"
		elif type == "menuC":
			self.animation = "menuC"

	'''
	Name: animateTalk
	Parameters: None
	Returns: None
	Purpose: Dynamically moves the components of the talk menu.
	'''
	def animateTalk(self):
		increment = 0
		if self.talkBgRect.center[0] > 500:
			increment = 20
		elif self.talkBgRect.center[0] > 440:
			increment = 10
		elif self.talkBgRect.center[0] <= 440 and not self.jitter:
			increment = 10
		elif self.talkBgRect.center[0] < 440 and self.jitter:
			increment = -10
		self.talkBgRect.x -= increment
		if self.talkBgRect.center[0] <= 420:
			self.jitter = True
		if self.talkBgRect.center[0] == 440 and self.jitter:
			self.animation = False

		if self.textboxRect.center[0] != 400:
			self.textboxRect.x += 40

		if self.speakerRect.center[0] != 500:
			self.speakerRect.x -= 30

	'''
	Name: animateExit
	Parameters: None
	Returns: None
	Purpose: Dynamically moves the background components to create an animation.
	'''
	def animateExit(self):
		increment = 0
		if self.talkBgRect.center[0] < 650:
			increment = 20
		else:
			increment = 40
			self.speakerRect.x += 30
		self.textboxRect.x -= increment
		self.talkBgRect.x += increment
		if self.speakerRect.x > 800:
			self.owner.talking = False

	'''
	Name: animateMenu
	Parameters: reverse:boolean
	Returns: None
	Purpose: Will move the menu box up and down depending on if reverse is True.
	'''
	def animateMenu(self, reverse = False):
		goal = 0
		if self.menuBgRect.topleft[1] > 500:
			increment = 50
		elif self.menuBgRect.topleft[1] > 200:
			increment = 30
		else:
			increment = 20
		if reverse:
			increment = increment *-1
			goal = 800
		self.menuBgRect.y -= increment
		if self.menuBgRect.y == goal:
			self.animation = False

	'''
	Name: animate
	Parameters: None
	Returns: None
	Purpose: Calls all relevant operations depending on what state the player is in and if an animation is playing.
	'''
	def animate(self):
		self.healthCalc(self.owner.health)
		if self.owner.talking:
			#animations
			if self.animation:
				if self.animation == "open":
					self.animateTalk()
				elif self.animation == "close":
					self.animateExit()
			else:
				self.nextDialogue()
				self.disText()
		#Paused
		elif self.owner.paused or self.animation == "menuC":
			if self.animation == "menuO":
				self.animateMenu()
			elif self.animation == "menuC":
				self.animateMenu(True)
			else:
				if not self.menuActivity:
					self.menuTxt, self.menuPos, confirm = self.menu(self.menuTxt, self.menuPos, self.menuOptions)
					if confirm:
						if self.menuOptions[self.menuPos] == "Resume":
							self.startAnimation("menuC")
							self.owner.tell_server("unpause")
							self.owner.paused = False
						elif self.menuOptions[self.menuPos] == "Items":
							self.menuActivity = "Items"
							self.inventoryOptions = []
							for item in self.owner.inventory:
								self.inventoryOptions.append(item.name)
							self.startTime = pygame.time.get_ticks()
							self.inventory()
						elif self.menuOptions[self.menuPos] == "Controls":
							self.menuActivity = "Controls"
							self.startTime = pygame.time.get_ticks()
				elif self.menuActivity == "Items":
					self.inventory()
				elif self.menuActivity == "Controls":
					self.controls()

	'''
	Name: menu
	Parameters: list:list, position:int, optionList:list
	Returns: list:list, position:int, boolean
	Purpose: This detects if the player has inputted to move or select an item in the list. If not then a list of images 
	of each option is created with the one being hovered over being coloured in red. The boolean that is returned 
	signifies if the player has or hasn't selected.
	'''
	def menu(self, list, position, optionList):
		keys = pygame.key.get_pressed()
		#confirm
		if keys[pygame.K_SPACE]:
			return list, position, True
		if self.cooldown:
			if pygame.time.get_ticks() - self.cooldown > 250:
				self.cooldown = False
		# Move up
		if keys[pygame.K_w] and position > 0 and not self.cooldown:
			position -= 1
			self.cooldown = pygame.time.get_ticks()
		# Move down
		if list:
			if keys[pygame.K_s] and position < len(list) - 1 and not self.cooldown:
				position += 1
				self.cooldown = pygame.time.get_ticks()
		# Creating options
		list = []
		for i in optionList:
			if len(list) == position:
				list.append(self.font.render(i, False, (255, 0, 0)))
			else:
				list.append(self.font.render(i, False, (255, 255, 255)))
		return list, position, False

	'''
	Name: nextDialogue
	Parameters: None
	Returns: None
	Purpose: Once a line of dialogue has finished being outputted, depending on whether there is a branch in the 
	path or not this function will either call a menu or progress to the next dialogue if it has detected an input. 
	'''
	def nextDialogue(self):
		if self.textDone:
			#Handles starting new dialogue if there is only 1 option in the dialogue graph
			if len(self.chatPos.neighbours) <= 1:
				keys = pygame.key.get_pressed()
				if keys[pygame.K_SPACE]:
					if self.chatPos.name != "end":
						self.chatPos = self.chatPos.neighbours[0]
						self.chatNumber = random.randint(0, len(self.chatPos.dialogue) - 1)
					else:
						self.owner.endTalk()
					self.letters = 0
					self.letterStart = 0
					self.textList = []
					self.continueDis = False
					self.textDone = False
				else:
					self.continueDis = True
			# Handles starting new dialogue if there is more than 1 option
			elif len(self.chatPos.neighbours) >= 2:

				list = []
				for n in self.chatPos.neighbours:
					if n.condition == False:
						list.append(n.option)
				self.optionDis, self.optionSelect, confirm = self.menu(self.optionDis, self.optionSelect, list)

				#Moves to next dialogue
				if confirm:
					self.chatPos = self.chatPos.neighbours[self.optionSelect]
					self.chatNumber = random.randint(0, len(self.chatPos.dialogue) - 1)
					self.letters = 0
					self.letterStart = 0
					self.optionSelect = 0
					self.textList = []
					self.textDone = False
					self.optionDis = False

		self.message = self.chatPos.dialogue[self.chatNumber]

	'''
	Name: inventory
	Parameters: None
	Returns: None
	Purpose: This displays items in the players inventory. It will the display details about the selected weapon and can 
	be changed by using menu function. Also in charge of selecting the players active weapon.
	'''
	def inventory(self):
		self.inventoryText, self.inventoryPos, confirm = self.menu(self.inventoryText, self.inventoryPos,
																   self.inventoryOptions)
		if confirm and self.owner.activeWeapon != self.owner.inventory[self.inventoryPos] and pygame.time.get_ticks() - self.startTime > 300:
			self.owner.activeWeapon = self.owner.inventory[self.inventoryPos]
			self.owner.tell_server("weapon", self.owner.activeWeapon.name)
		weapon = self.owner.inventory[self.inventoryPos]
		self.details = [[], weapon.damage]
		if self.owner.activeWeapon == weapon:
			self.details.append("Equipped")
		else:
			self.details.append("Press space to equip")
		message = ""
		count = 0
		start = 0
		for letter in weapon.description:
			if count - start > 30 and weapon.description[count - 1] == " ":
				self.details[0].append(message)
				message = ""
				start = count
				count = 0
			message += letter
			count += 1
		if message:
			self.details[0].append(message)
		for count in range(len(self.details[0])):
			self.details[0][count] = self.font.render(self.details[0][count], False, (255, 255, 255))
		self.details[1] = self.font.render("Damage: " + str(self.details[1]), False, (255, 255, 255))
		self.details[2] = self.font.render(self.details[2], False, (255, 255, 255))
		self.weaponImage = weapon.inventoryImage
		self.weaponRect = self.weaponImage.get_rect()
		self.weaponRect.center = (400, 200)
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			self.menuActivity = False

	def controls(self):
		self.controlOptions = []
		if self.owner.movementKeys["up"] == pygame.K_w:
			self.controlOptions.append("Movement keys:   WASD")
		else:
			self.controlOptions.append("Movement keys:   Arrows")

		self.controlText, blank, confirm = self.menu(self.controlText, 0, self.controlOptions)
		if confirm and pygame.time.get_ticks() - self.startTime > 300:
			if self.owner.movementKeys["up"] == pygame.K_w:
				self.owner.movementKeys = {"up":pygame.K_UP, "down":pygame.K_DOWN, "left":pygame.K_LEFT, "right":pygame.K_RIGHT}
			else:
				self.owner.movementKeys = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
			self.startTime = pygame.time.get_ticks()
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			self.menuActivity = False

	'''
	Name: disText
	Parameters: None
	Returns: None
	Purpose: Will display a message adding 1 letter each time the function is called until the full message is displayed.
	Will start a new line if the message is getting too long. 
	'''
	def disText(self):
		if self.letters != len(self.message):
			self.letters += 1
			if self.letters - self.letterStart > 40 and self.message[self.letters-1] == " ":
				self.textList.append(self.font.render(self.message[self.letterStart:self.letters], False, (255, 255, 255)))
				self.letterStart = self.letters
			self.text = self.font.render(self.message[self.letterStart:self.letters], False, (255, 255, 255))
		else:
			self.textDone = True


	'''
	Name: healthCalc
	Parameters: health:int
	Returns: None
	Purpose: This calculates the length of the healthbar and the amount of damage or heal that needs to be displayed (The 
	damage and heal bars lengths will slowly decrease). 
	'''
	def healthCalc(self, playerHealth):
		if self.displayHealth != playerHealth:
			#If health has been lost
			if playerHealth < self.displayHealth:
				self.displayDamage += self.displayHealth - playerHealth

				self.displayHealth = playerHealth
				#This prevents issues when drawing the bar MAYBE SHOULD SHIFT TAB BY ONE?
				if self.displayHealth < 0:
					self.displayHealth = 0
			#Health is gained
			else:
				self.displayHealth += 1
				self.displayHeal = playerHealth - self.displayHealth

		elif self.displayHeal > 0:
			self.displayHeal = 0


		#This decreases by one over time so that the damage bar slowly disappears
		if self.displayDamage > 0:
			self.displayDamage -= 1
			#This prevents the damage bar from exceeding the space
			if self.displayHealth + self.displayDamage > 100:
				self.displayDamage = 100- self.displayHealth

		self.health = pygame.transform.scale(self.health, ((self.displayHealth * 2) + 1, 40))
		self.damage = pygame.transform.scale(self.damage, ((self.displayDamage * 2) + 1, 40))
		self.heal = pygame.transform.scale(self.heal, ((self.displayHeal * 2) + 1, 40))

'''
Name: Camera
Purpose: This is used to ensure that when a player travels all entities including the map move appropriately to simulate
movement.
'''
class Camera:

	'''
	Name: __init__
	Parameters: owner:object
	Returns: None
	Purpose: This Constructs the camera and assigns it to the player so it follows them and not any other players in the server.
	'''
	def __init__(self, owner):
		self.owner = owner

	'''
	Name: reAdjust 
	Parameters: None
	Returns: None
	Purpose: This function is designed to readjust the camera so that it always follows the player unless they are at 
	an edge of the map.
	'''
	def reAdjust(self):
		if self.owner.rect.center[0] != (SCREEN_SIZE[0]//2)-1:#If not center
			if self.owner.mapX > (SCREEN_SIZE[0] // 2) - 1 and self.owner.mapX < (
					MAP_RES[0] - (SCREEN_SIZE[0] // 2)):  # Checks they aren't at border
				self.owner.mapX += self.owner.rect.center[0] - ((SCREEN_SIZE[0]//2)-1)#Adjusts the map coOrds if they are centered
			elif self.owner.mapX > MAP_RES[0] - SCREEN_SIZE[0]:#Identifies that they are at the right edge
				self.owner.mapX = (MAP_RES[0] - SCREEN_SIZE[0]) + self.owner.rect.center[0]#Adjusts the map coOrds if they are at the right border
			elif self.owner.mapX < SCREEN_SIZE[0]:#Identifies that they are at the left edge
				self.owner.mapX = self.owner.rect.center[0]#Adjusts the map coOrds if they are at the right border
			if self.owner.mapX > (SCREEN_SIZE[0] // 2) - 1 and self.owner.mapX < (
					MAP_RES[0] - (SCREEN_SIZE[0] // 2)):  # Checks they arent at border
				self.owner.rect.center = ((SCREEN_SIZE[0] // 2)-1, self.owner.rect.center[1])#Only changes the rect x coOrdinate if not at border

		if self.owner.rect.center[1] != (SCREEN_SIZE[1]//2)-1:#If not center
			if self.owner.mapY > (SCREEN_SIZE[1] // 2) - 1 and self.owner.mapY < (
					MAP_RES[1] - (SCREEN_SIZE[1] // 2)):  # Checks they aren't at border
				self.owner.mapY += self.owner.rect.center[1] - ((SCREEN_SIZE[1]//2)-1)#Adjusts the map coOrds if they are centered
			elif self.owner.mapY > MAP_RES[1] - SCREEN_SIZE[1]:#Identifies that they are at the right edge
				self.owner.mapY = (MAP_RES[1] - SCREEN_SIZE[1]) + self.owner.rect.center[1]#Adjusts the map coOrds if they are at the right border
			elif self.owner.mapY < SCREEN_SIZE[1]:#Identifies that they are at the left edge
				self.owner.mapY = self.owner.rect.center[1]#Adjusts the map coOrds if they are at the right border
			if self.owner.mapY > (SCREEN_SIZE[1] // 2) - 1 and self.owner.mapY < (
					MAP_RES[1] - (SCREEN_SIZE[1] // 2)):  # Checks they arent at border
				self.owner.rect.center = (self.owner.rect.center[0], (SCREEN_SIZE[1] // 2)-1)#Only changes the rect x coOrdinate if not at border

	'''
	Name: worldAdjust 
	Parameters: screen:rect, world:Object, characterList:spriteGroup, enemyList:spriteGroup, npcList:spriteGroup
	Returns: None
	Purpose: This readjusts any other players, enemies and NPCs in the world.
	'''
	def worldAdjust(self, screen, world, characterList, enemyList, npcList):
		worldX = self.owner.rect.center[0]-self.owner.mapX
		worldY = self.owner.rect.center[1]-self.owner.mapY
		world.x, world.y = worldX, worldY
		for character in characterList:
			if character != self.owner:
				character.rect.center = (worldX + character.mapX, worldY + character.mapY)
		for npc in npcList:
			npc.rect.center = (worldX + npc.mapX, worldY + npc.mapY)
		for enemy in enemyList:
			enemy.rect.center = (worldX + enemy.mapX, worldY + enemy.mapY)

	'''
	Name: bulletAdjust
	Parameters: bulletList:spriteGroup, explosionList:spriteGroup
	Returns: None
	Purpose: This readjusts any projectiles in the world
	'''
	def bulletAdjust(self, bulletList, explosionList):
		worldX = self.owner.rect.center[0]-self.owner.mapX
		worldY = self.owner.rect.center[1]-self.owner.mapY
		for bullet in bulletList:
			bullet.rect.center = (worldX + bullet.mapX, worldY + bullet.mapY)
		for explosion in explosionList:
			explosion.rect.center = (worldX + explosion.mapX, worldY + explosion.mapY)

	'''
	Name: obstacleAdjust
	Parameters: obstacleList:spriteGroup
	Returns: None
	Purpose: This readjusts any obstacles in the world
	'''
	def obstacleAdjust(self, obstacleList):
		worldX = self.owner.rect.center[0]-self.owner.mapX
		worldY = self.owner.rect.center[1]-self.owner.mapY
		for obstacle in obstacleList:
			obstacle.rect.center = (worldX + obstacle.mapX, worldY + obstacle.mapY)

npcList = pygame.sprite.Group()
enemyList = pygame.sprite.Group()
characters = pygame.sprite.Group()
obstacleList = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()

'''
Name: Bullet
Purpose: This is a projectile which can deal damage and travel across the map.
'''
class Bullet(pygame.sprite.Sprite):

	'''
	Name: __init__
	Parameters: x:integer, y:integer, direction:tuple
	Returns: None
	Purpose: This constructs the bullet. It takes in the direction of the bullet as a vector so it knows how much to
	increment the x and y coordinates by.
	'''
	def __init__(self,x,y,direction, owner, damage):
		super().__init__()
		self.width = 5
		self.height = 5
		self.image = pygame.surface.Surface((self.width,self.height))
		self.image.fill(WHITE)
		pygame.draw.rect(self.image,(0,0,0),(0,0,self.width,self.height))
		self.rect = self.image.get_rect()
		self.rect.center = x, y
		self.mapX = x
		self.mapY = y
		self.direction = direction
		self.damage = damage
		self.owner = owner

	'''
	Name: update
	Parameters: enemyList:spriteGroup, obstacleList:spriteGroup, serverSide:boolean
	Returns: enemy.id:int, self.damage:int
	Purpose: This increments the x and y co-ordinates as well as checking if the bullet has collided. If the bullet has
	passed the edge of the map or collided it will kill itself and deal any necessary damage.
	'''
	def update(self, enemyList, obstacleList, serverSide=False):
		self.mapX += self.direction[0]
		self.mapY += self.direction[1]
		for enemy in enemyList:
			if checkCollision(self.mapX - 2, self.mapX + 2, self.mapY - 2, self.mapY + 2,
							  enemy.mapX - (enemy.width//2), enemy.mapX + (enemy.width//2), enemy.mapY - (enemy.height//2), enemy.mapY + (enemy.height//2)):
				if self.owner:
					bullets.remove(self)
					self.kill()
					return enemy.id, self.damage

				bullets.remove(self)
				self.kill()

		for obstacle in obstacleList:
			if checkCollision(self.mapX - 2, self.mapX + 2, self.mapY - 2, self.mapY + 2,
							  obstacle.mapX - (obstacle.width//2), obstacle.mapX + (obstacle.width//2), obstacle.mapY - (obstacle.height//2), obstacle.mapY + (obstacle.height//2)):
				bullets.remove(self)
				self.kill()

		if self.mapY < 0 or self.mapY> MAP_RES[1] or self.mapX< 0 or self.mapX > MAP_RES[0]:#If outside the map
			bullets.remove(self)
			self.kill()


'''
Name: Explosion
Purpose: An area that deals damage before disappearing.
'''
class Explosion(pygame.sprite.Sprite):

	'''
	Name: __init__
	Parameters: x:integer, y:integer, rectX:int, rectY:int
	Returns: None
	Purpose: Constructs an explosion.
	'''
	def __init__(self,x,y, rectX, rectY):
		super().__init__()
		self.mapX, self.mapY = x, y
		self.width, self.height = TILE_SIZE*7, TILE_SIZE*7
		self.explosionTime = pygame.time.get_ticks()

		self.image = pygame.surface.Surface((self.height, self.width))
		#This makes the initial surface transparent
		self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

		#Adds two circles representing the different levels of damage
		pygame.draw.circle(self.image, (255, 0, 0), (self.width//2, self.height//2), self.height // 2)
		pygame.draw.circle(self.image, (255, 255, 0), (self.width // 2, self.height // 2), (self.height//2) // 2)

		self.rect = self.image.get_rect()
		self.rect.center = rectX, rectY

	'''
	Name: update
	Parameters: players:dict, serverSide:boolean
	Returns: boolean, data:list
	Purpose: This checks collisions and kills the explosion if it has ended.
	'''
	def update(self,players=False, serverSide = False):
		if serverSide:
			data = self.collisionCheck(players)

		if pygame.time.get_ticks() - self.explosionTime > 250:
			if serverSide:
				return ("kill", data)
			else:
				explosions.remove(self)
				self.kill()
		else:
			if not serverSide:
				self.image.set_alpha(self.image.get_alpha()-19)
			else:
				return (False, data)

	'''
	Name: collisionCheck
	Parameters: players:dict
	Returns: victims:list
	Purpose: This checks if a player is colliding with the explosion's rect. It then assigns damage based of the distance 
	the player is from the center.
	'''
	def collisionCheck(self, players):
		victims = []
		for p in players:
			player = players[p]
			if checkCollision(player.mapX-20, player.mapX+20, player.mapY-20, player.mapY+20,
							  self.mapX-(self.width//2), self.mapX+(self.width//2), self.mapY-(self.height//2), self.mapY+(self.height//2)) and pygame.time.get_ticks() - player.invincible >800 or not player.invincible:
				distance = math.sqrt(((player.mapX - self.mapX) ** 2) + ((player.mapY - self.mapY) ** 2))
				# Close proximity damage
				if distance - 20 < (self.height // 2) // 2:
					victims.append({"id":player.connection, "damage":40})
				# Far proximity damage
				elif distance - 20 < self.height // 2:
					victims.append({"id": player.connection, "damage": 10})

		if victims != []:
			return victims
		else:
			return False
		# collisions = pygame.sprite.spritecollide(self, players, False)
		# if collisions != []:
		# 	for col in collisions:
		# 		distance = math.sqrt(((col.mapX - self.mapX)**2)+((col.mapY - self.mapY)**2))
		# 		#Close proximity damage
		# 		if distance - col.height < (self.height//2)//2:
		# 			col.takeDamage(40)
		# 		#Far proximity damage
		# 		elif distance - col.height < self.height//2:
		# 			col.takeDamage(10)


'''
Name: Wall
Purpose: This is an obstacle which can't be passed through but can be destroyed.
'''
class Wall(pygame.sprite.Sprite):

	'''
	Name: __init__
	Parameters: x:integer, y:integer
	Returns: None
	Purpose: Constructor.
	'''
	def __init__(self,x,y):
		super().__init__()
		self.hp = 10
		self.width = TILE_SIZE
		self.height = TILE_SIZE
		self.image = pygame.surface.Surface((TILE_SIZE,TILE_SIZE))
		self.image.fill(WHITE)
		pygame.draw.rect(self.image,(0,0,0),(0,0,self.width,self.height))
		self.rect = self.image.get_rect()
		self.mapX = x
		self.mapY = y
		self.rect.center = x, y

	'''
	Name: takeDamage
	Parameters: None
	Returns: None
	Purpose: This makes the wall take damage. If it's health reaches zero then it is destroyed.
	'''
	def takeDamage(self):
		self.hp -= 1
		if self.hp < 0:
			obstacleList.remove(self)
			self.kill()
		if self.hp < 4:
			pygame.draw.rect(self.image, RED, (0, 0, self.width, self.height))
		elif self.hp < 7:
			pygame.draw.rect(self.image, GREEN, (0, 0, self.width, self.height))

	'''
	Name: __repr__
	Parameters: None
	Returns: string
	Purpose: Used for testing purposes.
	'''
	def __repr__(self):
		return f"{self.mapX}, {self.mapY}, wall"

'''
Name: Character
Purpose: This is what the player controls. This class is also used for any other players that are playing online.
'''
class Character(pygame.sprite.Sprite):
	idcount = 0

	'''
	Name: __init__
	Parameters: x:integer, y:integer, conn:connection, serverSide:boolean, id:int
	Returns: None
	Purpose: Constructor for player characters.
	'''
	def __init__(self,x,y,conn=None, serverSide = False, id = False):
		super().__init__()
		self.width = TILE_SIZE
		self.height = TILE_SIZE
		self.deadImage = pygame.image.load("Assets/ded.png")
		self.deadImage = pygame.transform.scale(self.deadImage, (self.width, self.height))
		self.aliveImage = pygame.image.load("Assets/rocket.png")
		self.aliveImage = pygame.transform.scale(self.aliveImage,(self.width,self.height))
		self.image = self.aliveImage
		self.rect = self.image.get_rect()
		self.rect.center = ((SCREEN_SIZE[0]//2)-1, (SCREEN_SIZE[1]//2)-1)
		self.mapX = x
		self.mapY = y
		self.direction = "UP"
		self.connection = conn
		if not serverSide:
			self.camera = Camera(self)
			self.hud = Hud(self)
		if serverSide:
			self.id = Character.idcount
			Character.idcount += 1
		else:
			self.id = id
		self.health = 100
		self.invincible = False
		self.talking = False
		self.talkCooldown = False
		self.dead = False
		self.confirm = False
		self.revive = False
		self.paused = False
		self.inventory = []
		self.activeWeapon = False
		self.movementKeys = {"up":pygame.K_w, "down":pygame.K_s, "left":pygame.K_a, "right":pygame.K_d}

	'''
	Name: fire
	Parameters: data:list
	Returns: None
	Purpose: This creates a bullet which travels in the direction of the cursor. It also informs the server so a shot is
	fired on other player's screens.
	'''
	def fire(self, data=False):
		if not data:
			angle = self.activeWeapon.calcGunAngle()
			start, bulletList = self.activeWeapon.fire()
			self.tell_server("projectile", (start, bulletList, angle))
			owner = True
		else:
			start = data[0]
			bulletList = data[1]
			owner = False
			self.activeWeapon.angle = data[2]
		for bullet in bulletList:
			bullets.add(Bullet(start[0], start[1], bullet, owner, self.activeWeapon.damage))

	'''
	Name: tell_server
	Parameters: action:string, data:list
	Returns: None
	Purpose: This function sends a message to the server so that the same action can be completed on other player's 
	games.
	'''
	def tell_server(self, action, data =  None):
		if self.connection != None:
			if action == "move":
				packet = {"command":"MOVE","data":{"xPos":self.mapX, "yPos":self.mapY}}
			elif action == "projectile":
				packet = {"command": "PROJECTILE", "data": {"start":data[0], "bulletList":data[1], "angle":data[2]}}
			elif action == "weapon":
				packet = {"command": "WEAPONSWAP", "data": {"weapon": data}}
			elif action == "hit":
				packet = {"command": "ENEMYHIT", "data": {"id": data[0], "damage": data[1]}}
			elif action == "kill":
				packet = {"command": "CONFIRMATION", "data": {"id": data}}
			elif action == "death":
				packet = {"command": "DEATHCONFIRMATION"}
			elif action == "revived":
				packet = {"command": "REVCONFIRMATION"}
			elif action == "talkstop":
				packet = {"command": "TALKSTOP"}
			elif action == "pause":
				packet = {"command": "PAUSE"}
			elif action == "unpause":
				packet = {"command": "UNPAUSE"}
			elif action == "revive":
				packet = {"command": "REVIVAL", "data": {"idList": data}}
			self.connection.send((json.dumps(packet) + "#").encode())


	'''
	Name: move
	Parameters: obstacles:spriteGroup
	Returns: None
	Purpose: This checks if a player can move or whether they will collide with a wall. If the player is moving in 
	multiple directions it will lower the velocity. 
	'''
	def move(self, obstacles):
		if not self.talking and not self.dead and not self.paused:
			keys = pygame.key.get_pressed()
			velocity = 6
			if keys[self.movementKeys["right"]] == True:#Account for diagonal speed
				if keys[self.movementKeys["up"]] == True or keys[self.movementKeys["down"]] == True:
					velocity = math.floor(velocity *0.7)


			elif keys[self.movementKeys["left"]] == True:
				if keys[self.movementKeys["up"]] == True or keys[self.movementKeys["down"]] == True:
					velocity =  math.floor(velocity *0.7)


			if keys[self.movementKeys["up"]] == True:
				self.rect.y -= velocity
				#self.mapY -= velocity
				self.direction = "UP"
				if pygame.sprite.spritecollide(self, obstacles, False):
					self.rect.y += velocity
					#self.mapY += velocity
				if self.rect.y <0:
					self.rect.y = 0
					#self.mapY = 0
				# if frame
				self.tell_server("move")

			if keys[self.movementKeys["down"]]:
				self.rect.y += velocity
				#self.mapY += velocity
				self.direction = "DOWN"
				if pygame.sprite.spritecollide(self, obstacles,False):
					self.rect.y -= velocity
					#self.mapY -= velocity
				if self.rect.y > SCREEN_SIZE[1]-self.height:
					self.rect.y = SCREEN_SIZE[1]-self.height
					#self.mapY = SCREEN_SIZE[1]-self.height
				self.tell_server("move")

			if keys[self.movementKeys["left"]]:
				self.rect.x -= velocity
				# self.mapX -= math.floor(velocity)
				self.direction = "LEFT"
				if pygame.sprite.spritecollide(self, obstacles,False):
					self.rect.x += velocity
					# self.mapX += velocity
				if self.rect.x < 0:
					self.rect.x = 0
					# self.mapX = 0
				self.tell_server("move")

			if keys[self.movementKeys["right"]]:
				self.rect.x += velocity
				# self.mapX += velocity
				self.direction = "RIGHT"
				if pygame.sprite.spritecollide(self, obstacles,False):
					self.rect.x -= velocity
					# self.mapX -= velocity
				if self.rect.x > SCREEN_SIZE[0]-self.width:
					self.rect.x = SCREEN_SIZE[0]-self.width
					# self.mapX = SCREEN_SIZE[0]-self.width
				self.tell_server("move")

	'''
	Name: takeDamage
	Parameters: damage:int, serverSide:boolean
	Returns: None
	Purpose: If enough time has passed since last time the player had been damaged by an enemy, they will take damage.
	'''
	def takeDamage(self, damage, serverSide=False):
		if serverSide:
			if pygame.time.get_ticks() - self.invincible >800 or not self.invincible:
				self.health -= damage
				if self.health < 0:
					self.health = 0
				self.invincible = pygame.time.get_ticks()
		else:
			self.health -= damage
			if self.health < 0:
				self.health = 0

	'''
	Name: checkTalk
	Parameters: npcs:spriteGroup
	Returns: npc:object
	Purpose: This will check if a player has collided with an NPC and wether their talk cooldown has ended.
	'''
	def checkTalk(self, npcs):
		if self.talkCooldown:
			if pygame.time.get_ticks() - self.talkCooldown > 1000:
				self.talkCooldown = False
		if not self.talking and not self.dead and not self.talkCooldown and not self.paused:
			count = 0
			while count != len(pygame.sprite.Group.sprites(npcs)):
				npc = pygame.sprite.Group.sprites(npcs)[count]
				if checkCollision(self.mapX -(self.width//2), self.mapX +(self.width//2), self.mapY -(self.height//2), self.mapY +(self.height//2),
								  npc.mapX -(npc.width//2), npc.mapX +(npc.width//2), npc.mapY -(npc.height//2), npc.mapY +(npc.height//2)):
					self.talking = npc
					return npc
				count += 1

		return False

	'''
	Name: endTalk
	Parameters: serverSide:boolean
	Returns: None
	Purpose: Tells the server and removes the player from the NPC's customers.
	'''
	def endTalk(self, serverSide=False):
		if serverSide:
			self.talking.removeCustomer(self.id)
			self.talking = False
		else:
			self.tell_server("talkstop")
			self.hud.startAnimation("close")
		self.talkCooldown = pygame.time.get_ticks()

	'''
	Name: die
	Parameters: serverSide:boolean
	Returns: None
	Purpose: Changes the player's state and sprites.
	'''
	def die(self, serverSide=False):
		self.dead = pygame.time.get_ticks()
		if not serverSide:
			self.health = 0
			self.deadSprite()
		if self.talking:
			self.endTalk(serverSide)

	'''
	Name: deadSprite
	Parameters: None
	Returns: None
	Purpose: Changes the players sprite to a dead one.
	'''
	def deadSprite(self):
		self.image = self.deadImage

	'''
	Name: checkRevive
	Parameters: players:list
	Returns: None
	Purpose: This will check if the player is holding the revive key and will revive any nearby players.
	'''
	def checkRevive(self, players):
		checked = False
		reviveList = []
		for player in players:
			if player != self and player.dead and not self.talking and not self.dead and not self.paused:
				distance = math.sqrt(((player.mapX - self.mapX) ** 2) + ((player.mapY - self.mapY) ** 2))
				if distance < 70:
					self.revive = True
					checked = True
					reviveList.append(player.id)

		if not checked:
			self.revive = False
		else:
			keys = pygame.key.get_pressed()
			if keys[pygame.K_r]:
				self.tell_server("revive", reviveList)
				for player in players:
					if player.id in reviveList:
						player.reviveSelf()

	'''
	Name: reviveSelf
	Parameters: None
	Returns: None
	Purpose: Changes the players sprites, states and sets the players health to 50.
	'''
	def reviveSelf(self):
		self.health = 50
		self.dead = False
		self.image = self.aliveImage

	'''
	Name: checkPause
	Parameters: None
	Returns: None
	Purpose: Will check if the player is holding down the pause button and if so will activate the pause menu.
	'''
	def checkPause(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			if not self.talking and not self.paused:
				self.hud.startAnimation("menu")
				self.paused = True
				self.tell_server("pause")

'''
Name: Gun
Purpose: Parent class for all gun related weapons.
'''
class Gun(pygame.sprite.Sprite):

	'''
	Name: __init__
	Parameters: image:str, damage:int, owner:object, cooldown:int, name:str, resize:tuple
	Returns: None
	Purpose: Constructor.
	'''
	def __init__(self, image, damage, owner, offset, cooldown, name, resize = False):
		super().__init__()
		self.origImage = pygame.image.load(image)
		if resize:
			self.origImage = pygame.transform.scale(self.origImage, resize)
		self.image = self.origImage
		self.rect = self.image.get_rect()
		self.rect.center = (-1000, -1000)
		self.damage = damage
		self.owner = owner
		self.lastShot = pygame.time.get_ticks()
		self.cooldown = cooldown
		self.barrel = (0, 0)#This is where the bullets come from
		self.barrelMap = (0, 0)#This is the coordinate for where the bullet spawns
		self.offset = offset#(Used to reposition gun for facing, used for calculating the distance the center should be away from the player, used for determining the barrels position)
		self.trajectory = (0, 0)
		self.name = name
		self.angle = 0

	'''
	Name: calcGunAngle
	Parameters: calc:boolean
	Returns: None
	Purpose: Calculates the position rotation and location of the barrel of the gun based of the player's mouse position.
	'''
	def calcGunAngle(self, calc = False):
		lastPos = (self.rect.center)
		try:
			if not calc:
				mouse = pygame.mouse.get_pos()
				adjacent = mouse[0] - self.owner.rect.centerx
				opposite = mouse[1] - self.owner.rect.centery

				self.angle = math.degrees(math.atan2(opposite, adjacent))

			#Offsets the angle so the gun faces the cursor
			self.angle += self.offset[0]
			self.angle = self.angle % 360

			self.image = pygame.transform.rotate(self.origImage, -self.angle)
			self.rect = self.image.get_rect()

			#Positions the image
			x = self.owner.rect.centerx + self.offset[2] * math.cos(math.radians(self.angle))
			y = self.owner.rect.centery + self.offset[2] * math.sin(math.radians(self.angle))
			self.rect.center = (x, y)

			#Resumes original angle
			self.angle -= self.offset[0]
			self.angle = self.angle % 360

			x = self.owner.rect.centerx + self.offset[1] * math.cos(math.radians(self.angle+2))
			y = self.owner.rect.centery + self.offset[1] * math.sin(math.radians(self.angle+2))
			self.barrel = (x, y)
			x = self.owner.mapX + self.offset[1] * math.cos(math.radians(self.angle))
			y = self.owner.mapY + self.offset[1] * math.sin(math.radians(self.angle))
			self.barrelMap = (x, y)

			x = self.owner.rect.centerx + 150 * math.cos(math.radians(self.angle+2))
			y = self.owner.rect.centery + 150 * math.sin(math.radians(self.angle+2))
			self.trajectory = (x, y)

			return self.angle

		except:
			print("exception")
			self.rect.center = lastPos

	'''
	Name: fire
	Parameters: None
	Returns: self.barrelMap:tuple, bulletList:sprite group
	Purpose: Creates a bullet and calculates the angle and velocity
	'''
	def fire(self):
		#calculates the increment
		increment = [self.barrel[0] - self.trajectory[0], self.barrel[1] - self.trajectory[1]]
		hypotenuse = math.sqrt((increment[0] ** 2) + (increment[1] ** 2))
		#Divides hypotenuse to work out the amount of seconds it would take to reach the mouse
		seconds = hypotenuse / 10
		bulletList = []
		for count in range(2):
			increment[count] = increment[count] * -1
			increment[count] = increment[count] / seconds #divides the length of the distance by the number of seconds to get the distance per second
		bulletList.append(increment)
		return self.barrelMap, bulletList

	'''
	Name: draw
	Parameters: screen:rect
	Returns: None
	Purpose: Displays the gun's sprite.
	'''
	def draw(self, screen):
		screen.blit(self.image, self.rect)

'''
Name: Pistol
Purpose: Type of gun that shoots singular shots.
'''
class Pistol(Gun):

	'''
	Name: __init__
	Parameters: owner:object
	Returns: None
	Purpose: Constructor.
	'''
	def __init__(self, owner):
		super().__init__("Assets/gun.png", 5, owner, (8, 70, 50), 100, "Pistol")
		self.description = "A basic pistol for basic people."
		self.inventoryImage = pygame.image.load("Assets/gun.png")
		self.inventoryImage = pygame.transform.scale(self.inventoryImage, (400, 300))

'''
Name: Shotgun
Purpose: Shoots a random spray of bullets.
'''
class Shotgun(Gun):

	'''
	Name: __init__
	Parameters: owner:object
	Returns: None
	Purpose: Constructor.
	'''
	def __init__(self, owner):
		super().__init__("Assets/shotgun.png", 4, owner, (4, 110, 65), 100, "Shotgun", (110, 40))
		self.description = "A shotgun which shoots a powerful but inaccurate barage of bullets."
		self.inventoryImage = pygame.image.load("Assets/shotgun.png")
		self.inventoryImage = pygame.transform.scale(self.inventoryImage, (440, 160))

	'''
	Name: fire
	Parameters: None
	Returns: self.barrelMap:tuple, bulletList:sprite group
	Purpose: Modified version of the fire function which instead shoots a random spray of several bullets.
	'''
	def fire(self):
		#calculates the increment
		increment = [self.barrel[0] - self.trajectory[0], self.barrel[1] - self.trajectory[1]]
		hypotenuse = math.sqrt((increment[0] ** 2) + (increment[1] ** 2))
		#Divides hypotenuse to work out the amount of seconds it would take to reach the mouse
		seconds = hypotenuse / 10
		bulletList = []
		for count in range(2):
			increment[count] = increment[count] * -1
			increment[count] = increment[count] / seconds #divides the length of the distance by the number of seconds to get the distance per second
		for count in range(6):
			bulletList.append([])
			for i in increment:
				alter = random.randint(-4, 4)
				bulletList[-1].append(i+alter)
			check = False
			for item in bulletList[count]:
				if item > 4:
					check = True
			else:
				while not check:
					bulletList[count] = []
					for i in increment:
						alter = random.randint(-4, 4)
						bulletList[-1].append(i + alter)
					for item in bulletList[count]:
						if item > 4 or item < -4:
							check = True
		return self.barrelMap, bulletList

'''
Name: priorityQueue
Purpose: This is a priority queue
'''
class priorityQueue:

	'''
	Name: __init__
	Parameters: None
	Returns: None
	Purpose: Constructor for priority queues usesd for pathfinding.
	'''
	def __init__(self):
		self.queue = []
		self.length = len(self.queue)-1#Stores the index of the last item in the list

	'''
	Name: enqueue
	Parameters: item:list
	Returns: None
	Purpose: This adds an item to the queue and orders it based of it's combined heuristic. 
	'''
	def enqueue(self, item):#This adds an item and readjusts
		if self.length == -1:
			self.queue.append(item)

		elif self.queue[self.length-1][2] <= item[2]:
			self.queue.append(item)

		else:
			inserted = False
			count = 0
			while inserted == False:
				if self.queue[count][2] >= item[2]:
					self.queue.insert(count, item)
					inserted = True
				count += 1
		self.length += 1

	'''
	Name: dequeue
	Parameters: None
	Returns: item:List
	Purpose: Removes the first item in the queue then returns it.
	'''
	def dequeue(self):#This removes the first item and returns it
		if self.length != -1:#Ensures the queue is not empty
			item = self.queue[0]
			self.queue.remove(item)
			self.length -= 1
			return item

	'''
	Name: insert
	Parameters: path:list
	Returns: None
	Purpose: This removes an item then enqueues a version of the same item with the updated combined heuristic.
	'''
	def insert(self, path):
		for item in self.queue:
			if item[0] == path[0]:
				self.queue.remove(item)
		self.length -= 1
		self.enqueue(path)


'''
Name: Enemy
Purpose: This is an enemy which tracks and attacks any players in it's vision.
'''
class Enemy(pygame.sprite.Sprite):

	'''
	Name: __init__
	Parameters: x:int, y:int, id:int
	Returns: None
	Purpose: Constructor for enemies.
	'''
	def __init__(self, x, y, id):
		super().__init__()
		self.width = TILE_SIZE
		self.height = TILE_SIZE
		self.image = pygame.image.load("Assets/evilBear.png")
		self.image_orig = pygame.image.load("Assets/evilBear.png")
		self.image_orig = pygame.transform.scale(self.image_orig, (self.width, self.height))
		self.image = pygame.transform.scale(self.image,(self.width,self.height))
		self.rect = self.image.get_rect()
		self.rect.center = 1000, 1000
		self.mapX = x
		self.mapY = y
		self.direction = "UP"
		self.startTime = False
		self.id = id
		self.health = 100

	'''
	Name: locate
	Parameters: playerList:spriteGroup, world:object
	Returns: successfulPath:list
	Purpose: This makes use of an A* search and a priority queue in order to find a path from the enemy to any players 
	in the enemies' sightings.
	'''
	def locate(self, playerList, world):#could do with Nodes
		shortestDis = False
		target = False
		if playerList:#If a player has been sighted
			for player in playerList:#This finds the closest one
				distance = (self.mapX - player.mapX), (self.mapY - player.mapY)
				hypotenuse = math.sqrt((distance[0]**2)+(distance[1]**2))
				if not shortestDis or hypotenuse < shortestDis:
					target = player
					shortest = hypotenuse
		#A* search
		paths = priorityQueue()# structure of each entry - [Node name, path cost, combined heuristic (distance from Node + The path ), 	[Node paths]]
		goalNode = world.nodes[target.mapY//TILE_SIZE][target.mapX//TILE_SIZE]
		solution = False
		X = int(self.mapX//TILE_SIZE)#Need the location of the enemy in reference to Nodes
		Y = int(self.mapY//TILE_SIZE)
		paths.enqueue([world.nodes[Y][X], 0, math.sqrt(((world.nodes[Y][X].mapX - target.mapX)**2)+((world.nodes[Y][X].mapY - target.mapY)**2)), []])#This is the start node
		visited = []
		while not solution:
			current = paths.dequeue()
			visited.append(current[0])
			for neighbour in current[0].neighbours:#Evaluates all neighbours to be queued
				# if neighbour:
				present = False#This checks to ensure that there aren't duplicates of the same Node being added

				#Checking the node hasn't already been checked or queued
				if neighbour in visited:
					present = True
				else:
					for path in paths.queue:
						if neighbour == path[0]:
							present = True
							#This updates a path if a shorter route to the same node is found
							if path[1] > current[1] + abs(math.sqrt(((neighbour.mapX - target.mapX)**2)+((neighbour.mapY - target.mapY)**2))):
								path[1] = current[1] + abs(math.sqrt(((neighbour.mapX - target.mapX)**2)+((neighbour.mapY - target.mapY)**2)))
								path[2] = abs(math.sqrt(((neighbour.mapX - current[0].mapX) ** 2)+((neighbour.mapY - current[0].mapY)**2))) + abs(math.sqrt(((neighbour.mapX - target.mapX)**2)+((neighbour.mapY - target.mapY)**2)))
								pathNodes = current[3]
								pathNodes.append(current[0])
								path[3] = pathNodes
								paths.insert(path)



				if not present:
					pathNodes = current[3][:]
					pathNodes.append(current[0])
					if neighbour == goalNode:
						solution = True
						successfulPath = pathNodes
						del(paths)
						return successfulPath

					else:
						paths.enqueue([neighbour, abs(math.sqrt(((neighbour.mapX - current[0].mapX) ** 2)+((neighbour.mapY - current[0].mapY)**2))) + current[1],#this calculates the hypotenuse from one neighbour to another then adds the previous nodes path cost
								  abs(math.sqrt(((neighbour.mapX - current[0].mapX) ** 2)+((neighbour.mapY - current[0].mapY)**2))) + abs(math.sqrt(((neighbour.mapX - target.mapX)**2)+((neighbour.mapY - target.mapY)**2))), pathNodes])

			if current[0] == goalNode:
				solution = True

	'''
	Name: travel
	Parameters: path:list
	Returns: None
	Purpose: This moves the enemy closer to the next node in the path it is given. If it is close enough to the player
	it will now begin exploding.
	'''
	def travel(self, path):
		#This stops the game from breaking if the player is so close that no path is returned
		if path:
			# Starts the attack sequence although maybe I should move this somewhere else?
			if len(path) < 2 and not self.startTime:
				self.startTime = pygame.time.get_ticks()

			#Moves the enemy
			else:
				nextNode = path[1]
				sides = [self.mapX - nextNode.mapX, self.mapY - nextNode.mapY]

				hypotenuse = math.sqrt((sides[0]**2)+(sides[1]**2))
				seconds = hypotenuse//2
				# return self.mapX, nextNode.mapX, self.mapY, nextNode.mapY
				for count in range(len(sides)):
					sides[count] = sides[count] * -1
					sides[count] = sides[count] // seconds


				self.mapX += sides[0]
				self.mapY += sides[1]

	'''
	Name: attack
	Parameters: None
	Returns: None
	Purpose: This starts an explosion when enough time has passed since the enemy has begun destructing. It will then 
	spawn an explosion and destroy itself. 
	'''
	def attack(self):
		#Creates explosion
		e = Explosion(self.mapX, self.mapY, self.rect.center[0], self.rect.center[1])
		explosions.add(e)
		enemyList.remove(self)
		self.kill()

	'''
	Name: takeDamage
	Parameters: damage:int
	Returns: None
	Purpose: Damages the enemy.
	'''
	def takeDamage(self, damage):
		self.health -= damage
		if self.health <= 0:
			self.health = 0

'''
Name: ServerEnemy
Purpose: An enemy which is modified to work on serverSide.
'''
class ServerEnemy:
	idcount = 0
	directions = [(-1, -1), (0, -2), (1, -1), (2, 0), (1, 1), (0, 2), (-1, 1), (-2, 0)]

	'''
	Name: __init__
	Parameters: x:integer, y:integer
	Returns: None
	Purpose: Constructor.
	'''
	def __init__(self, x, y):
		self.width = TILE_SIZE
		self.height = TILE_SIZE
		self.mapX = x
		self.mapY = y
		self.startTime = False
		self.health = 100
		self.id = ServerEnemy.idcount
		ServerEnemy.idcount += 1
		self.confirm = False
		self.walking = 0
		self.direction = (4, 4)
		self.targets = []

	'''
	Name: locate
	Parameters: playerList:dict, serverNodes:list
	Returns: solution:list
	Purpose: Performs an A* search if a player has been spotted. Enemies will prioritise the closest visible enemy.
	'''
	def locate(self, playerList, serverNodes):
		for p in playerList:
			distance = (self.mapX - playerList[p].mapX), (self.mapY - playerList[p].mapY)
			hypotenuse = math.sqrt((distance[0] ** 2) + (distance[1] ** 2))
			if hypotenuse < 500 and not playerList[p].dead:
				self.targets.append([playerList[p], hypotenuse])
			elif playerList[p] in self.targets:
				for t in self.targets:
					if t[0] == playerList[p]:
						if playerList[p].dead:
							self.targets.remove(t)
						else:
							t[1] = hypotenuse

		if len(self.targets) > 0:#If a player has been sighted
			shortestDis = False
			target = False
			for p in self.targets:#This finds the closest one
				if not shortestDis or p[1] < shortestDis:
					target = p[0]
					shortestDis = p[1]

			#A* search
			paths = priorityQueue()# structure of each entry - [Node name, path cost, combined heuristic (distance from Node + The path ), 	[Node paths]]
			goalNode = serverNodes[target.mapY//TILE_SIZE][target.mapX//TILE_SIZE]
			solution = False
			X = int(self.mapX//TILE_SIZE)#Need the location of the enemy in reference to Nodes
			Y = int(self.mapY//TILE_SIZE)
			if not serverNodes[Y][X]:
				count = 0
				flip = False
				while not serverNodes[Y][X]:
					if count < 2:
						if not flip:
							X -= 1
							count += 1
						elif flip:
							Y -= 1
							count += 1
					else:
						count = 0
						flip = not flip

			paths.enqueue([serverNodes[Y][X], 0, math.sqrt(((serverNodes[Y][X].mapX - target.mapX)**2)+((serverNodes[Y][X].mapY - target.mapY)**2)), []])#This is the start node
			visited = []
			while not solution:
				current = paths.dequeue()
				visited.append(current[0])
				for neighbour in current[0].neighbours:#Evaluates all neighbours to be queued
					# if neighbour:
					present = False#This checks to ensure that there aren't duplicates of the same Node being added

					#Checking the node hasn't already been checked or queued
					if neighbour in visited:
						present = True
					else:
						for path in paths.queue:
							if neighbour == path[0]:
								present = True
								#This updates a path if a shorter route to the same node is found
								if path[1] > current[1] + abs(math.sqrt(((neighbour.mapX - target.mapX) ** 2) + ((neighbour.mapY - target.mapY) ** 2))):
									path[1] = current[1] + abs(math.sqrt(((neighbour.mapX - target.mapX) ** 2) + ((neighbour.mapY - target.mapY) ** 2)))
									path[2] = abs(math.sqrt(((neighbour.mapX - current[0].mapX) ** 2) + ((neighbour.mapY - current[0].mapY) ** 2))) + abs(math.sqrt(((neighbour.mapX - target.mapX) ** 2) + ((neighbour.mapY - target.mapY) ** 2)))
									pathNodes = current[3]
									pathNodes.append(current[0])
									path[3] = pathNodes
									paths.insert(path)



					if not present:
						pathNodes = current[3][:]
						pathNodes.append(current[0])
						if neighbour == goalNode:
							solution = True
							successfulPath = []
							for node in pathNodes:
								successfulPath.append(node)
							del(paths)
							return successfulPath

						else:
							paths.enqueue([neighbour, abs(math.sqrt(((neighbour.mapX - current[0].mapX) ** 2)+((neighbour.mapY - current[0].mapY)**2))) + current[1],#this calculates the hypotenuse from one neighbour to another then adds the previous nodes path cost
									  abs(math.sqrt(((neighbour.mapX - current[0].mapX) ** 2)+((neighbour.mapY - current[0].mapY)**2))) + abs(math.sqrt(((neighbour.mapX - target.mapX)**2)+((neighbour.mapY - target.mapY)**2))), pathNodes])
				if current[0] == goalNode:
					solution = True
		else:
			return False

	'''
	Name: travel
	Parameters: path:list
	Returns: packet:dict
	Purpose: This determines the enemy's activity. This could be dieing moving or attacking.
	'''
	def travel(self, path):
		packet =  None
		if self.health <= 0:
			packet = (self.id, "ENEMYDIE")
		#This stops the game from breaking if the player is so close that no path is returned

		elif self.startTime:
			return None

		elif path:
			# Starts the attack sequence although maybe I should move this somewhere else?
			if len(path) < 2:
				if not self.startTime:
					self.startTime = pygame.time.get_ticks()
				packet = (self.id, "ENEMYATTACK")

			#Moves the enemy
			else:
				nextNode = path[1]
				sides = [self.mapX - nextNode.mapX, self.mapY - nextNode.mapY]

				hypotenuse = math.sqrt((sides[0]**2)+(sides[1]**2))
				seconds = hypotenuse//2
				# return self.mapX, nextNode.mapX, self.mapY, nextNode.mapY
				for count in range(len(sides)):
					sides[count] = sides[count] * -1
					sides[count] = sides[count] // seconds


				self.mapX += sides[0]
				self.mapY += sides[1]
				packet = (self.id, "ENEMYMOVE", self.mapX, self.mapY)
		else:
			if pygame.time.get_ticks() - self.walking >= 800:
				self.walking = pygame.time.get_ticks()
				r = random.randint(0, 7)
				self.direction = ServerEnemy.directions[r]

			self.mapX += self.direction[0]
			self.mapY += self.direction[1]

			packet = (self.id, "ENEMYMOVE", self.mapX, self.mapY)

		return packet

	'''
	Name: takeDamage
	Parameters: damage:int
	Returns: None
	Purpose: Takes damage away from health.
	'''
	def takeDamage(self, damage):
		self.health -= damage
		if self.health <= 0:
			self.health = 0

'''
Name: nodeSetup
Parameters: obstacleList:spriteGroup, nodes:list
Returns: None
Purpose: This scans over the whole map to check if there are any collisions with obstacles.
if it doesn't detect a collision in the given area then it will initialise a Node for pathfinding and store it in the
nodes variable(It is a two dimensional list). It will then pass through every node in this 2D list to
establish neighbours if there are any near it. Neighbours are added in a way that tries to ensure entities don't get
stuck on corners.
'''
def nodeSetup(obstacleList, nodes):
	sortedObstacles = []
	for obstacle in obstacleList:
		#If the list is empty
		if len(sortedObstacles) == 0:
			sortedObstacles.append(obstacle)

		#If this obstacle is the farthest in the list
		elif sortedObstacles[len(sortedObstacles)-1].mapX <= obstacle.mapX:
			sortedObstacles.append(obstacle)

		#Linear insert
		else:
			inserted = False
			count = 0
			while inserted == False:
				if obstacle.mapX < sortedObstacles[count].mapX:
					sortedObstacles.insert(count, obstacle)
					inserted = True
				else:
					count += 1

	for y in range (MAP_WIDTH*(SCREEN_SIZE[1]//TILE_SIZE)):
		for x in range (MAP_WIDTH*(SCREEN_SIZE[0]//TILE_SIZE)):
			collision = False
			for obstacle in obstacleList:
				if checkCollision(x*40, x*40 + TILE_SIZE, y*40, y*40 + TILE_SIZE, obstacle.mapX - (obstacle.width//2), obstacle.mapX + (obstacle.width//2), obstacle.mapY - (obstacle.height//2), obstacle.mapY + (obstacle.height//2)):
					collision = True
			if not collision:
				nodes[y][x] = Node((x*TILE_SIZE) + (TILE_SIZE//2),(y*TILE_SIZE) + (TILE_SIZE//2))

	# This assigns the neighbours to the nodes
	for y in range(MAP_WIDTH * (SCREEN_SIZE[1] // TILE_SIZE)):  # This calculates the amount of cells wide each tile is then multiplies it by the number of tiles
		for x in range(MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE)):
			if nodes[y][x] != False:  # If there is a node present
				if x != 0:  # If not at a border
					if nodes[y][x - 1]:  # if the node is not false
						nodes[y][x].left = nodes[y][x - 1]
						nodes[y][x].neighbours.append(nodes[y][x].left)

					if y != 0:
						if nodes[y][x - 1] != False and nodes[y - 1][
							x] != False:  # This is in order to prevent clipping through corners
							if nodes[y - 1][x - 1]:
								nodes[y][x].topLeft = nodes[y - 1][x - 1]
								nodes[y][x].neighbours.append(nodes[y][x].topLeft)

					if y != MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE) - 1:
						if nodes[y][x - 1] != False and nodes[y + 1][x] != False:
							if nodes[y + 1][x - 1]:
								nodes[y][x].bottomLeft = nodes[y + 1][x - 1]
								nodes[y][x].neighbours.append(nodes[y][x].bottomLeft)

				if x != MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE) - 1:
					if nodes[y][x + 1]:
						nodes[y][x].right = nodes[y][x + 1]
						nodes[y][x].neighbours.append(nodes[y][x].right)

					if y != 0:
						if nodes[y][x + 1] != False and nodes[y - 1][x] != False:
							if nodes[y - 1][x + 1]:
								nodes[y][x].topRight = nodes[y - 1][x + 1]
								nodes[y][x].neighbours.append(nodes[y][x].topRight)

					if y != MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE) - 1:
						if nodes[y][x + 1] != False and nodes[y + 1][x] != False:
							if nodes[y + 1][x + 1]:
								nodes[y][x].bottomRight = nodes[y + 1][x + 1]
								nodes[y][x].neighbours.append(nodes[y][x].bottomRight)

				if y != 0:
					if nodes[y - 1][x]:
						nodes[y][x].up = nodes[y - 1][x]
						nodes[y][x].neighbours.append(nodes[y][x].up)

				if y != MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE) - 1:
					if nodes[y + 1][x]:
						nodes[y][x].down = nodes[y + 1][x]
						nodes[y][x].neighbours.append(nodes[y][x].down)

	return nodes
