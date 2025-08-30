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

		self.speaker = pygame.image.load("Assets/speaker.png")
		self.speaker = pygame.transform.scale(self.speaker, (800, 800))
		self.speakerRect = self.speaker.get_rect()
		self.speakerRect.center = 860, 400

		self.textbox = pygame.Surface((800, 250), pygame.SRCALPHA)
		self.textbox.fill((0, 0, 0, 150))
		self.textboxRect = self.textbox.get_rect()
		self.textboxRect.bottomright = (0, 800)

		self.jitter = False
		self.letters = 0
		self.font = pygame.font.SysFont('Times New Roman', 40)

		self.message = "My name is EDWIN, I made the mimic."
		self.text = self.font.render((""), False, (255, 255, 255))
		self.textRect = self.text.get_rect()


	'''
	Name: draw
	Parameters: screen:rect
	Returns: None
	Purpose: Displays the Hud
	'''
	def draw(self, screen):
		self.healthCalc(self.owner.health)

		screen.blit(self.background, (TILE_SIZE // 4 + 10, TILE_SIZE // 4 + 10))
		screen.blit(self.damage,((TILE_SIZE//4) + 10 + (self.displayHealth * 2) - 1, TILE_SIZE//4 + 10))
		screen.blit(self.heal, ((TILE_SIZE // 4) + 10 + (self.displayHealth * 2) - 1, TILE_SIZE // 4 + 10))
		screen.blit(self.health,(TILE_SIZE//4 + 10 - 1, TILE_SIZE//4 + 10))
		screen.blit(self.healthbar, (TILE_SIZE//4, TILE_SIZE//4))

		if self.owner.talking:
			screen.blit(self.talkBg, self.talkBgRect)
			screen.blit(self.speaker, self.speakerRect)
			screen.blit(self.textbox, self.textboxRect)
			if not self.animation:
				screen.blit(self.text, self.textRect)

		if self.owner.revive:
			screen.blit(self.revive, self.reviveRect)

	def startAnimation(self, type):
		if type == "open":
			self.jitter = False
			self.animation = "open"
		elif type == "close":
			self.animation = "close"

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

	def disText(self):
		if self.letters != len(self.message):
			self.letters += 1
			self.text = self.font.render(self.message[:self.letters], False, (255, 255, 255))
			self.textRect = self.text.get_rect()
			self.textRect.topleft = 10, 560

	'''
	Name: healthCalc
	Parameters: health:int
	Returns: None
	Purpose: This calculates the length of the healthbar and the amount of damage that needs to be displayed (The 
	damage bars length will slowly decrease). 
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
	Parameters: screen:rect, world:Object, characterList:spriteGroup, enemyList:spriteGroup
	Returns: None
	Purpose: This readjusts any other players or enemies in the world.
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
	Parameters: bulletList:spriteGroup
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
	def __init__(self,x,y,direction):
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
		self.damage = 5

	'''
	Name: update
	Parameters: None
	Returns: None
	Purpose: This increments the x and y co-ordinates as well as checking if the bullet has collided. If the bullet has
	passed the edge of the map or collided it will kill itself
	'''
	def update(self, enemyList, serverSide=False):
		self.mapX += self.direction[0]
		self.mapY += self.direction[1]
		for enemy in enemyList:
			if checkCollision(self.mapX - 2, self.mapX + 2, self.mapY - 2, self.mapY + 2,
							  enemy.mapX - (enemy.width//2), enemy.mapX + (enemy.width//2), enemy.mapY - (enemy.height//2), enemy.mapY + (enemy.height//2)):
				if serverSide:
					return True, enemy

				else:
					bullets.remove(self)
					self.kill()

		if self.mapY < 0 or self.mapY> MAP_RES[1] or self.mapX< 0 or self.mapX > MAP_RES[0]:#If outside the map
			if serverSide:
				return False, "kill"

			else:
				bullets.remove(self)
				self.kill()

		return False, None

	def collisionCheck(self, enemyList, serverSide=False):
		for enemy in enemyList:
			# print(self.mapX - 2, self.mapX + 2, self.mapY - 2, self.mapY + 2,
			# 				  enemy.mapX - (enemy.width//2), enemy.mapX + (enemy.width//2), enemy.mapY - (enemy.height//2), enemy.mapY + (enemy.height//2))
			# print(checkCollision(self.mapX - 2, self.mapX + 2, self.mapY - 2, self.mapY + 2,
			# 				  enemy.mapX - (enemy.width//2), enemy.mapX + (enemy.width//2), enemy.mapY - (enemy.height//2), enemy.mapY + (enemy.height//2)))
			if checkCollision(self.mapX - 2, self.mapX + 2, self.mapY - 2, self.mapY + 2,
							  enemy.mapX - (enemy.width//2), enemy.mapX + (enemy.width//2), enemy.mapY - (enemy.height//2), enemy.mapY + (enemy.height//2)):
				if serverSide:
					return True, enemy

				else:
					bullets.remove(self)
					self.kill()

		if self.mapY < 0 or self.mapY> MAP_RES[1] or self.mapX< 0 or self.mapX > MAP_RES[0]:#If outside the map
			if serverSide:
				return False, "kill"

			else:
				bullets.remove(self)
				self.kill()

		return False, None
		


'''
Name: Explosion
Purpose: An area that deals damage before disappearing.
'''
class Explosion(pygame.sprite.Sprite):

	'''
	Name: __init__
	Parameters: x:integer, y:integer
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
	Parameters: None
	Returns: None
	Purpose: This checks if the player is colliding with the rect it then checks the distance from the center and
	applies the appropriate amount of damage. It then deletes the explosion if enough time has passed but otherwise just
	lowers the alpha to make it look like it's fading away.
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
	Parameters: x:integer, y:integer, conn:connection
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
		self.dead = False
		self.confirm = False
		self.revive = False

	'''
	Name: fire
	Parameters: coOrds:list, calculated:boolean
	Returns: None
	Purpose: This creates a bullet which travels in the direction of the cursor. It also informs the server so a shot is
	fired on other player's screens.
	'''
	def fire(self, coOrds, calculated=False):
		if calculated == False:
			sides = [self.rect.x-coOrds[0], self.rect.y-coOrds[1]] #calculates the vector
			hypotenuse = math.sqrt((sides[0]**2)+(sides[1]**2))
			#Divides the hypotenuse to work out how many seconds it will take to reach the mouse
			seconds = hypotenuse/10
			for count in range(len(sides)):
				sides[count] = sides[count]*-1
				sides[count] = sides[count]/seconds #divides the sides by the amount of seconds to work out how much the axis should increment per second
			self.tell_server("projectile", sides)
		else:
			sides = coOrds
		b = Bullet(self.mapX, self.mapY, sides)
		bullets.add(b)

	# '''
	# Name: rotate
	# Parameters: None
	# Returns: None
	# Purpose: This rotates the players image depending on the direction they have last travelled in.
	# '''
	# def rotate(self):
	# 	angle = 0
	# 	if self.direction == "DOWN":
	# 		angle = 180
	# 	elif self.direction == "LEFT":
	# 		angle = 90
	# 	elif self.direction == "RIGHT":
	# 		angle = 270
	#
	# 	self.image = pygame.transform.rotate(self.image_orig,angle)

	'''
	Name: tell_server
	Parameters: action:string, coOrds:list
	Returns: None
	Purpose: This function sends a message to the server so that the saem action can be completed on other player's 
	games.
	'''
	def tell_server(self, action, data =  None):
		if self.connection != None:
			if action == "move":
				packet = {"command":"MOVE","data":{"xPos":self.mapX, "yPos":self.mapY}}
			elif action == "projectile":
				packet = {"command": "PROJECTILE", "data": {"xPos": self.mapX, "yPos":self.mapY, "coOrds":data}}
			elif action == "kill":
				packet = {"command": "CONFIRMATION", "data": {"id": data}}
			elif action == "death":
				packet = {"command": "DEATHCONFIRMATION"}
			elif action == "revived":
				packet = {"command": "REVCONFIRMATION"}
			elif action == "talk":
				packet = {"command": "TALK", "data": {"id": data}}
			elif action == "revive":
				packet = {"command": "REVIVAL", "data": {"idList": data}}
			self.connection.send((json.dumps(packet) + "#").encode())


	'''
	Name: move
	Parameters: None
	Returns: None
	Purpose: This checks if a player can move or wether they will collide with a wall. If the player is moving in 
	multiple directions it will lower the velocity. 
	'''
	def move(self, obstacles):
		if not self.talking and not self.dead:
			keys = pygame.key.get_pressed()
			velocity = 6
			if keys[pygame.K_d] == True:#Account for diagonal speed
				if keys[pygame.K_w] == True or keys[pygame.K_s] == True:
					velocity = math.floor(velocity *0.7)


			elif keys[pygame.K_a] == True:
				if keys[pygame.K_w] == True or keys[pygame.K_s] == True:
					velocity =  math.floor(velocity *0.7)


			if keys[pygame.K_w] == True:
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

			if keys[pygame.K_s]:
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

			if keys[pygame.K_a]:
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

			if keys[pygame.K_d]:
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
	Parameters: damage:int
	Returns: None
	Purpose: If enough time has passed since last damaged the enemy will take damage
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

	def checkTalk(self, npcs):
		if not self.talking and not self.dead:
			count = 0
			while count != len(pygame.sprite.Group.sprites(npcs)):
				npc = pygame.sprite.Group.sprites(npcs)[count]
				if checkCollision(self.mapX -(self.width//2), self.mapX +(self.width//2), self.mapY -(self.height//2), self.mapY +(self.height//2),
								  npc.mapX -(npc.width//2), npc.mapX +(npc.width//2), npc.mapY -(npc.height//2), npc.mapY +(npc.height//2)):
					self.talking = npc
					return npc
				count += 1

		return False

	def endTalk(self, serverSide=False):
		if serverSide:
			self.talking.removeCustomer(self.connection)
			self.talking = False
		else:
			self.hud.startAnimation("close")


	def die(self, serverSide=False):
		self.dead = pygame.time.get_ticks()
		if not serverSide:
			self.health = 0
			self.deadSprite()
		if self.talking:
			self.endTalk(serverSide)

	def deadSprite(self):
		self.image = self.deadImage

	def checkRevive(self, players):
		checked = False
		reviveList = []
		for player in players:
			if player != self and player.dead and not self.talking and not self.dead:
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

	def reviveSelf(self):
		self.health = 50
		self.dead = False
		self.image = self.aliveImage


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
	Parameters: x:int, y:int
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
		self.rect.center = ((SCREEN_SIZE[0]//2)-1, (SCREEN_SIZE[1]//2)-1)
		self.mapX = 1000 + x
		self.mapY = 1000 + y
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

	def takeDamage(self, damage):
		self.health -= damage
		if self.health <= 0:
			self.health = 0

class ServerEnemy:
	idcount = 0
	directions = [(-1, -1), (0, -2), (1, -1), (2, 0), (1, 1), (0, 2), (-1, 1), (-2, 0)]
	def __init__(self, x, y):
		self.width = TILE_SIZE
		self.height = TILE_SIZE
		self.mapX = 1000 + x
		self.mapY = 1000 + y
		self.startTime = False
		self.health = 100
		self.id = ServerEnemy.idcount
		ServerEnemy.idcount += 1
		self.confirm = False
		self.walking = 0
		self.direction = (4, 4)
		self.targets = []

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

	def takeDamage(self, damage):
		self.health -= damage
		if self.health <= 0:
			self.health = 0

class NPC(pygame.sprite.Sprite):
	#class variables
	idcount = 0
	directions = {1:"left", 2:"up", 3:"right", 4:"down"}
	def __init__(self, x, y, id=False):
		super().__init__()
		self.width = TILE_SIZE
		self.height = TILE_SIZE
		self.image = pygame.image.load("Assets/NPC.png")
		self.image_orig = pygame.image.load("Assets/NPC.png")
		self.image_orig = pygame.transform.scale(self.image_orig, (self.width, self.height))
		self.image = pygame.transform.scale(self.image,(self.width,self.height))
		self.rect = self.image.get_rect()
		self.rect.center = -400, -400
		self.mapX = x
		self.mapY = y
		if id:
			self.id = id
		else:
			self.id = NPC.idcount
		NPC.idcount += 1
		self.activity = ["idol", pygame.time.get_ticks()]#[activity, time started]
		self.customers = []

	def determineState(self):
		if self.activity[0] != "talking":
			# This swaps states
			if pygame.time.get_ticks() - self.activity[1] >= 2000 and self.activity[0] == "idol":
				direction = self.directions[random.randint(1, 4)]
				self.activity = ["moving", pygame.time.get_ticks(), direction]
			elif pygame.time.get_ticks() - self.activity[1] >= 1000 and self.activity[0] == "moving":
				self.activity = ["idol", pygame.time.get_ticks()]

			# Action
			if self.activity[0] == "moving":
				if self.activity[2] == "left":
					self.mapX -= 2
				elif self.activity[2] == "up":
					self.mapY -= 2
				elif self.activity[2] == "right":
					self.mapX += 2
				elif self.activity[2] == "down":
					self.mapY += 2
				return self.id, self.mapX, self.mapY

		return False

	def addCustomer(self, customer):
		self.customers.append(customer)
		if self.activity[0] != "talking":
			self.activity[0] = "talking"

	def removeCustomer(self, customer):
		self.customers.remove(customer)
		if len(self.customers) == 0:
			self.activity[0] = "idol"


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
