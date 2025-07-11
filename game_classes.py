import pygame, json, math, MapGen

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
		self.img, self.obstacleList = mapGen.finalise()
		# Convert the PIL Image to a pygame Surface so that it can blit-ed without any issues
		img_bytes = self.img.tobytes()
		img_size = self.img.size
		img_mode = self.img.mode
		self.img = pygame.image.fromstring(img_bytes, img_size, img_mode)#fromstring requires the bytes for the image, the size and the mode
		self.tileMap = mapGen.textMap
		self.worldSurface = pygame.Surface((MAP_RES))
		self.worldSurface.blit(self.img, (0, 0))
		self.nodes = [[False for count in range(MAP_WIDTH*(SCREEN_SIZE[1]//TILE_SIZE))] for i in range(MAP_WIDTH*(SCREEN_SIZE[0]//TILE_SIZE))]#Establishes a plain grid

	# '''
	# Name: setupNodes
	# Parameters: obstacleList:spriteGroup
	# Returns: None
	# Purpose: This scans over the whole map to check if there are any collisions with obstacles.
	# if it doesn't detect a collision in the given area then it will initialise a Node for pathfinding and store it in
	# the self.nodes variable(It is a two dimensional list). It will then pass through every node in this 2D list to
	# establish neighbours if there are any near it. Neighbours are added in a way that tries to ensure entities don't get
	# stuck on corners.
	# '''
	# def setupNodes(self, obstacleList):
	# 	colDetector = pygame.sprite.Sprite()#This is an object that is used to seeif anything is near where it is placed
	# 	colDetector.rect = pygame.Rect(0, 0, 10, 10)
	# 	for y in range(MAP_WIDTH * (SCREEN_SIZE[1] // TILE_SIZE)):#This calculates the amount of cells wide each tile is then multiplies it by the number of tiles
	# 		for x in range(MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE)):
	# 			colDetector.rect.center = (x * TILE_SIZE) + (TILE_SIZE // 2), (y * TILE_SIZE) + (TILE_SIZE // 2)
	# 			collisions = pygame.sprite.spritecollide(colDetector, obstacleList, False)
	# 			if not collisions:
	# 				self.nodes[y][x] = Node((x * TILE_SIZE) + (TILE_SIZE // 2), (y * TILE_SIZE) + (TILE_SIZE // 2))
	#
	# 	#This assigns the neighbours to the nodes
	# 	for y in range(MAP_WIDTH*(SCREEN_SIZE[1]//TILE_SIZE)):#This calculates the amount of cells wide each tile is then multiplies it by the number of tiles
	# 		for x in range(MAP_WIDTH*(SCREEN_SIZE[0]//TILE_SIZE)):
	# 			if self.nodes[y][x] != False:#If there is a node present
	# 				if x != 0:#If not at a border
	# 					if self.nodes[y][x - 1]:# if the node is not false
	# 						self.nodes[y][x].left = self.nodes[y][x - 1]
	# 						self.nodes[y][x].neighbours.append(self.nodes[y][x].left)
	#
	# 					if y != 0:
	# 						if self.nodes[y][x-1] != False and self.nodes[y-1][x] != False:#This is in order to prevent clipping through corners
	# 							if self.nodes[y - 1][x - 1]:
	# 								self.nodes[y][x].topLeft = self.nodes[y - 1][x - 1]
	# 								self.nodes[y][x].neighbours.append(self.nodes[y][x].topLeft)
	#
	# 					if y != MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE) - 1:
	# 						if self.nodes[y][x-1] != False and self.nodes[y+1][x] != False:
	# 							if self.nodes[y + 1][x - 1]:
	# 								self.nodes[y][x].bottomLeft = self.nodes[y + 1][x - 1]
	# 								self.nodes[y][x].neighbours.append(self.nodes[y][x].bottomLeft)
	#
	# 				if x != MAP_WIDTH*(SCREEN_SIZE[0]//TILE_SIZE) - 1:
	# 					if self.nodes[y][x+1]:
	# 						self.nodes[y][x].right = self.nodes[y][x+1]
	# 						self.nodes[y][x].neighbours.append(self.nodes[y][x].right)
	#
	# 					if y != 0:
	# 						if self.nodes[y][x+1] != False and self.nodes[y-1][x] != False:
	# 							if self.nodes[y - 1][x + 1]:
	# 								self.nodes[y][x].topRight = self.nodes[y - 1][x + 1]
	# 								self.nodes[y][x].neighbours.append(self.nodes[y][x].topRight)
	#
	# 					if y != MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE) - 1:
	# 						if self.nodes[y][x+1] != False and self.nodes[y+1][x] != False:
	# 							if self.nodes[y +1][x + 1]:
	# 								self.nodes[y][x].bottomRight = self.nodes[y +1][x + 1]
	# 								self.nodes[y][x].neighbours.append(self.nodes[y][x].bottomRight)
	#
	# 				if y != 0:
	# 					if self.nodes[y-1][x]:
	# 						self.nodes[y][x].up = self.nodes[y-1][x]
	# 						self.nodes[y][x].neighbours.append(self.nodes[y][x].up)
	#
	# 				if y != MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE) - 1:
	# 					if self.nodes[y+1][x]:
	# 						self.nodes[y][x].down = self.nodes[y+1][x]
	# 						self.nodes[y][x].neighbours.append(self.nodes[y][x].down)

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
		#Health bar section
		self.displayHealth = 100
		self.displayDamage = 0
		# dimensions are 110 by 30
		self.healthbar = pygame.image.load("healthbar.png")
		self.healthbar = pygame.transform.scale(self.healthbar,(220, 60))
		#colours
		self.healthBgColour = (25, 25, 25)
		self.white = (255, 255, 255)
		self.healthColour = (255, 120, 90)

		self.health = pygame.surface.Surface((self.displayHealth, 40))
		self.health.fill(self.healthColour)

		self.damage = pygame.surface.Surface((self.displayHealth, 40))
		self.damage.fill(self.white)

		self.background = pygame.surface.Surface((self.displayHealth*2, 40))
		self.background.fill(self.healthBgColour)

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
		screen.blit(self.health,(TILE_SIZE//4 + 10 - 1, TILE_SIZE//4 + 10))
		screen.blit(self.healthbar, (TILE_SIZE//4, TILE_SIZE//4))

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
				#This ensures that damage does not begin increasing
				if self.displayHealth > 0:
					self.displayDamage += self.displayHealth - playerHealth

				self.displayHealth = playerHealth
				#This prevents issues when drawing the bar MAYBE SHOULD SHIFT TAB BY ONE?
				if self.displayHealth < 0:
					self.displayHealth = 0

		#This decreases by one over time so that the damage bar slowly disappears
		self.displayDamage -= 1
		if self.displayDamage < 0:
			self.displayDamage = 0

		elif self.displayHealth+ self.displayDamage > 100:
			self.displayDamage = 100- self.displayHealth

		self.health = pygame.transform.scale(self.health, ((self.displayHealth * 2) + 1, 40))
		self.damage = pygame.transform.scale(self.damage, ((self.displayDamage * 2) + 1, 40))

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
	def worldAdjust(self, screen, world, characterList, enemyList):
		worldX = self.owner.rect.center[0]-self.owner.mapX
		worldY = self.owner.rect.center[1]-self.owner.mapY
		world.x, world.y = worldX, worldY
		for character in characterList:
			if character != self.owner:
				character.rect.center = (worldX + character.mapX, worldY + character.mapY)
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

	'''
	Name: update
	Parameters: None
	Returns: None
	Purpose: This increments the x and y co-ordinates as well as checking if the bullet has collided. If the bullet has
	passed the edge of the map or collided it will kill itself
	'''
	def update(self):
		self.mapX += self.direction[0]
		self.mapY += self.direction[1]
		collisions = pygame.sprite.spritecollide(self,obstacleList,False)
		if collisions != []:
			for w in collisions:
				w.takeDamage()
				bullets.remove(self)
				self.kill()
		if self.mapY < 0 or self.mapY> MAP_RES[1]:
			bullets.remove(self)
			self.kill()
		if self.mapX< 0 or self.mapX > MAP_RES[0]:
			bullets.remove(self)
			self.kill()

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
	def update(self):
		collisions = pygame.sprite.spritecollide(self, characters, False)
		if collisions != []:
			for col in collisions:
				distance = math.sqrt(((col.mapX - self.mapX)**2)+((col.mapY - self.mapY)**2))
				#Close proximity damage
				if distance //4 < (self.height//2)//2:
					col.takeDamage(40)
				#Far proximity damage
				elif distance - col.height < self.height//2:
					col.takeDamage(10)

		if pygame.time.get_ticks() - self.explosionTime > 250:
			explosions.remove(self)
			self.kill()
		else:
			self.image.set_alpha(self.image.get_alpha()-19)

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

	'''
	Name: __init__
	Parameters: x:integer, y:integer, conn:connection
	Returns: None
	Purpose: Constructor for player characters.
	'''
	def __init__(self,x,y,conn=None):
		super().__init__()
		self.width = TILE_SIZE
		self.height = TILE_SIZE
		self.image = pygame.image.load("rocket.png")
		self.image_orig = pygame.image.load("rocket.png")#This one is always upright which is useful for rotating with movement
		self.image_orig = pygame.transform.scale(self.image_orig, (self.width, self.height))
		self.image = pygame.transform.scale(self.image,(self.width,self.height))
		self.rect = self.image.get_rect()
		self.rect.center = ((SCREEN_SIZE[0]//2)-1, (SCREEN_SIZE[1]//2)-1)
		self.mapX = x
		self.mapY = y
		self.direction = "UP"
		self.connection = conn
		self.camera = Camera(self)
		self.hud = Hud(self)
		self.health = 100
		self.invincible = False

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

	'''
	Name: rotate
	Parameters: None
	Returns: None
	Purpose: This rotates the players image depending on the direction they have last travelled in.
	'''
	def rotate(self):
		angle = 0
		if self.direction == "DOWN":
			angle = 180
		elif self.direction == "LEFT":
			angle = 90
		elif self.direction == "RIGHT":
			angle = 270

		self.image = pygame.transform.rotate(self.image_orig,angle)

	'''
	Name: tell_server
	Parameters: action:string, coOrds:list
	Returns: None
	Purpose: This function sends a message to the server so that the saem action can be completed on other player's 
	games.
	'''
	def tell_server(self, action, coOrds =  None):
		if self.connection != None:
			if action == "move":
				packet = {"command":"MOVE","data":{"xPos":self.mapX, "yPos":self.mapY}}
				self.connection.send((json.dumps(packet)+"#").encode())
			elif action == "projectile":
				packet = {"command": "PROJECTILE", "data": {"xPos": self.rect.x+(self.width//2)-2, "yPos":self.rect.y-2, "coOrds":coOrds}}
				self.connection.send((json.dumps(packet) + "#").encode())

	'''
	Name: move
	Parameters: None
	Returns: None
	Purpose: This checks if a player can move or wether they will collide with a wall. If the player is moving in 
	multiple directions it will lower the velocity. 
	'''
	def move(self):
		keys = pygame.key.get_pressed()
		velocity = 6
		if keys[pygame.K_RIGHT] == True:#Account for diagonal speed
			if keys[pygame.K_UP] == True or keys[pygame.K_DOWN] == True:
				velocity = math.floor(velocity *0.7)


		elif keys[pygame.K_LEFT] == True:
			if keys[pygame.K_UP] == True or keys[pygame.K_DOWN] == True:
				velocity =  math.floor(velocity *0.7)


		if keys[pygame.K_UP] == True:
			self.rect.y -= velocity
			#self.mapY -= velocity
			self.direction = "UP"
			self.rotate()
			if pygame.sprite.spritecollide(self, obstacleList, False):
				self.rect.y += velocity
				#self.mapY += velocity
			if self.rect.y <0:
				self.rect.y = 0
				#self.mapY = 0
			# if frame
			self.tell_server("move")

		if keys[pygame.K_DOWN]:
			self.rect.y += velocity
			#self.mapY += velocity
			self.direction = "DOWN"
			self.rotate()
			if pygame.sprite.spritecollide(self, obstacleList,False):
				self.rect.y -= velocity
				#self.mapY -= velocity
			if self.rect.y > SCREEN_SIZE[1]-self.height:
				self.rect.y = SCREEN_SIZE[1]-self.height
				#self.mapY = SCREEN_SIZE[1]-self.height
			self.tell_server("move")

		if keys[pygame.K_LEFT]:
			self.rect.x -= velocity
			# self.mapX -= math.floor(velocity)
			self.direction = "LEFT"
			self.rotate()
			if pygame.sprite.spritecollide(self, obstacleList,False):
				self.rect.x += velocity
				# self.mapX += velocity
			if self.rect.x < 0:
				self.rect.x = 0
				# self.mapX = 0
			self.tell_server("move")

		if keys[pygame.K_RIGHT]:
			self.rect.x += velocity
			# self.mapX += velocity
			self.direction = "RIGHT"
			self.rotate()
			if pygame.sprite.spritecollide(self, obstacleList,False):
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
	def takeDamage(self, damage):
		if pygame.time.get_ticks() - self.invincible >800 or not self.invincible:
			self.health -= damage
			if self.health < 0:
				self.health = 0
			self.invincible = pygame.time.get_ticks()


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

	# def destroy(self):
	# 	self.kill()

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
		self.image = pygame.image.load("evilBear.png")
		self.image_orig = pygame.image.load("evilBear.png")
		self.image_orig = pygame.transform.scale(self.image_orig, (self.width, self.height))
		self.image = pygame.transform.scale(self.image,(self.width,self.height))
		self.rect = self.image.get_rect()
		self.rect.center = ((SCREEN_SIZE[0]//2)-1, (SCREEN_SIZE[1]//2)-1)
		self.mapX = 1000 + x
		self.mapY = 1000 + y
		self.direction = "UP"
		self.startTime = False
		self.id = id

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

class ServerEnemy:
	idcount = 0
	def __init__(self, x, y):
		self.width = TILE_SIZE
		self.height = TILE_SIZE
		self.mapX = 1000 + x
		self.mapY = 1000 + y
		self.startTime = False
		self.health = 100
		self.id = ServerEnemy.idcount
		ServerEnemy.idcount += 1

	def locate(self, playerList, serverNodes):
		shortestDis = False
		target = False
		if playerList:#If a player has been sighted
			for player in playerList:#This finds the closest one
				distance =  (self.mapX - playerList[player]["location"][0]), (self.mapY - playerList[player]["location"][1])
				hypotenuse = math.sqrt((distance[0]**2)+(distance[1]**2))
				if not shortestDis or hypotenuse < shortestDis:
					target = playerList[player]
					shortestDis = hypotenuse

		#A* search
		paths = priorityQueue()# structure of each entry - [Node name, path cost, combined heuristic (distance from Node + The path ), 	[Node paths]]
		goalNode = serverNodes[target["location"][1]//TILE_SIZE][target["location"][0]//TILE_SIZE]
		solution = False
		X = int(self.mapX//TILE_SIZE)#Need the location of the enemy in reference to Nodes
		Y = int(self.mapY//TILE_SIZE)
		paths.enqueue([serverNodes[Y][X], 0, math.sqrt(((serverNodes[Y][X].mapX - target["location"][0])**2)+((serverNodes[Y][X].mapY - target["location"][1])**2)), []])#This is the start node
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
							if path[1] > current[1] + abs(math.sqrt(((neighbour.mapX - target["location"][0]) ** 2) + ((neighbour.mapY - target["location"][1]) ** 2))):
								path[1] = current[1] + abs(math.sqrt(((neighbour.mapX - target["location"][0]) ** 2) + ((neighbour.mapY - target["location"][1]) ** 2)))
								path[2] = abs(math.sqrt(((neighbour.mapX - current[0].mapX) ** 2) + ((neighbour.mapY - current[0].mapY) ** 2))) + abs(math.sqrt(((neighbour.mapX - target["location"][0]) ** 2) + ((neighbour.mapY - target["location"][1]) ** 2)))
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
								  abs(math.sqrt(((neighbour.mapX - current[0].mapX) ** 2)+((neighbour.mapY - current[0].mapY)**2))) + abs(math.sqrt(((neighbour.mapX - target["location"][0])**2)+((neighbour.mapY - target["location"][1])**2))), pathNodes])
			if current[0] == goalNode:
				solution = True

	def travel(self, path):
		#This stops the game from breaking if the player is so close that no path is returned
		if path:
			if self.health <= 0:
				packet = (self.id, "ENEMYDIE")

			# Starts the attack sequence although maybe I should move this somewhere else?
			elif len(path) < 2:
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

			return packet

	def take_Damage(self, damage):
		self.health -= damage
		if self.health <= 0:
			self.health = 0
			self.attack


def checkCollision(x1, x2, y1, y2, ox1, ox2, oy1, oy2):
	if ((x1 <= ox1 < x2) or (x1 < ox2 <= x2) or (ox1 < x1 < ox2)) and ((y1 <= oy1 < y2) or (y1 < oy2 <= y2) or (oy1 < y1 < oy2)):
		return True
	else:
		return False

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
