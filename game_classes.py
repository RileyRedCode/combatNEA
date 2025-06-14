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
		return f"{self.mapX},{self.mapY}"

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

	'''
	Name: setupNodes
	Parameters: obstacleList:spriteGroup
	Returns: None
	Purpose: This scans over the whole map to check if there are any collisions with obstacles.
	if it doesn't detect a collision in the given area then it will initialise a Node for pathfinding and store it in
	the self.nodes variable(It is a two dimensional list). It will then pass through every node in this 2D list to
	establish neighbours if there are any near it. Neighbours are added in a way that tries to ensure entities don't get
	stuck on corners.
	'''
	def setupNodes(self, obstacleList):
		colDetector = pygame.sprite.Sprite()#This is an object that is used to seeif anything is near where it is placed
		colDetector.rect = pygame.Rect(0, 0, 10, 10)
		for y in range(MAP_WIDTH * (SCREEN_SIZE[1] // TILE_SIZE)):#This calculates the amount of cells wide each tile is then multiplies it by the number of tiles
			for x in range(MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE)):
				colDetector.rect.center = (x * TILE_SIZE) + (TILE_SIZE // 2), (y * TILE_SIZE) + (TILE_SIZE // 2)
				collisions = pygame.sprite.spritecollide(colDetector, obstacleList, False)
				if not collisions:
					self.nodes[y][x] = Node((x * TILE_SIZE) + (TILE_SIZE // 2), (y * TILE_SIZE) + (TILE_SIZE // 2))

		#This assigns the neighbours to the nodes
		for y in range(MAP_WIDTH*(SCREEN_SIZE[1]//TILE_SIZE)):#This calculates the amount of cells wide each tile is then multiplies it by the number of tiles
			for x in range(MAP_WIDTH*(SCREEN_SIZE[0]//TILE_SIZE)):
				if self.nodes[y][x] != False:#If there is a node present
					if x != 0:#If not at a border
						if self.nodes[y][x - 1]:# if the node is not false
							self.nodes[y][x].left = self.nodes[y][x - 1]
							self.nodes[y][x].neighbours.append(self.nodes[y][x].left)

						if y != 0:
							if self.nodes[y][x-1] != False and self.nodes[y-1][x] != False:#This is in order to prevent clipping through corners
								if self.nodes[y - 1][x - 1]:
									self.nodes[y][x].topLeft = self.nodes[y - 1][x - 1]
									self.nodes[y][x].neighbours.append(self.nodes[y][x].topLeft)

						if y != MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE) - 1:
							if self.nodes[y][x-1] != False and self.nodes[y+1][x] != False:
								if self.nodes[y + 1][x - 1]:
									self.nodes[y][x].bottomLeft = self.nodes[y + 1][x - 1]
									self.nodes[y][x].neighbours.append(self.nodes[y][x].bottomLeft)

					if x != MAP_WIDTH*(SCREEN_SIZE[0]//TILE_SIZE) - 1:
						if self.nodes[y][x+1]:
							self.nodes[y][x].right = self.nodes[y][x+1]
							self.nodes[y][x].neighbours.append(self.nodes[y][x].right)

						if y != 0:
							if self.nodes[y][x+1] != False and self.nodes[y-1][x] != False:
								if self.nodes[y - 1][x + 1]:
									self.nodes[y][x].topRight = self.nodes[y - 1][x + 1]
									self.nodes[y][x].neighbours.append(self.nodes[y][x].topRight)

						if y != MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE) - 1:
							if self.nodes[y][x+1] != False and self.nodes[y+1][x] != False:
								if self.nodes[y +1][x + 1]:
									self.nodes[y][x].bottomRight = self.nodes[y +1][x + 1]
									self.nodes[y][x].neighbours.append(self.nodes[y][x].bottomRight)

					if y != 0:
						if self.nodes[y-1][x]:
							self.nodes[y][x].up = self.nodes[y-1][x]
							self.nodes[y][x].neighbours.append(self.nodes[y][x].up)

					if y != MAP_WIDTH * (SCREEN_SIZE[0] // TILE_SIZE) - 1:
						if self.nodes[y+1][x]:
							self.nodes[y][x].down = self.nodes[y+1][x]
							self.nodes[y][x].neighbours.append(self.nodes[y][x].down)

	'''
	Name: draw
	Parameters: screen:rect
	Returns: None
	Purpose: draws the map onto the screen
	'''
	def draw(self, screen):
		screen.blit(self.worldSurface, (self.x, self.y))

'''
Name: Camera
Purpose: This is used to ensure that when a player travels all entities including the map move appropriately to simulate
movement.
'''
class Camera:

	'''
	Name: __init__
	Parameters: Owner:class
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
	def bulletAdjust(self, bulletList):
		worldX = self.owner.rect.center[0]-self.owner.mapX
		worldY = self.owner.rect.center[1]-self.owner.mapY
		for bullet in bulletList:
			bullet.rect.center = (worldX + bullet.mapX, worldY + bullet.mapY)

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
		self.rect.x = x
		self.rect.y = y
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
		self.mapX = 1000 + x
		self.mapY = 1000 + y
		self.direction = "UP"
		self.connection = conn
		self.camera = Camera(self)

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
		# return
		# if self.direction == "UP":
		# 	b = Bullet(self.rect.x+(self.width//2)-2,self.rect.y-2,sides)
		# elif self.direction == "DOWN":
		# 	b = Bullet(self.rect.x + (self.width // 2) - 2, self.rect.y +(self.height // 2) - 2, sides)
		# elif self.direction == "LEFT":
		# 	b = Bullet(self.rect.x - 2, self.rect.y + (self.height // 2) - 2, sides)
		# else:
		# 	b = Bullet(self.rect.x + (self.width) - 2, self.rect.y + (self.height // 2) - 2, sides)

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
	Purpose: 
	'''
	def tell_server(self, action, coOrds =  None):
		if self.connection != None:
			if action == "move":
				packet = {"command":"MOVE","data":{"xPos":self.mapX, "yPos":self.mapY}}
				self.connection.send((json.dumps(packet)+"#").encode())
			elif action == "projectile":
				packet = {"command": "PROJECTILE", "data": {"xPos": self.rect.x+(self.width//2)-2, "yPos":self.rect.y-2, "coOrds":coOrds}}
				self.connection.send((json.dumps(packet) + "#").encode())

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


class priorityQueue:
	def __init__(self):
		self.queue = []
		self.length = len(self.queue)-1#Stores the index of the last item in the list

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

	def dequeue(self):#This removes the first item and returns it
		if self.length != -1:#Ensures the queue is not empty
			item = self.queue[0]
			self.queue.remove(item)
			self.length -= 1
			return item

	def insert(self, path):
		self.queue.remove(path)
		self.length -= 1
		self.enqueue(path)



	# def destroy(self):
	# 	self.kill()

class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
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
					if neighbour == goalNode:
						solution = True
						successfulPath = pathNodes
						return successfulPath

					else:
						pathNodes.append(current[0])
						paths.enqueue([neighbour, abs(math.sqrt(((neighbour.mapX - current[0].mapX) ** 2)+((neighbour.mapY - current[0].mapY)**2))) + current[1],#this calculates the hypotenuse from one neighbour to another then adds the previous nodes path cost
								  abs(math.sqrt(((neighbour.mapX - current[0].mapX) ** 2)+((neighbour.mapY - current[0].mapY)**2))) + abs(math.sqrt(((neighbour.mapX - target.mapX)**2)+((neighbour.mapY - target.mapY)**2))), pathNodes])

			if current[0] == goalNode:
				solution = True



	def travel(self, path):
		nextNode = path[1]
		if len(path) < 3:
			#write a function that make it attack
			pass

			# while self.mapX not in range(node.mapX-3, node.mapX+3) and self.mapY not in range(node.mapY-3, node.mapY+3):
		sides = [self.mapX - nextNode.mapX, self.mapY - nextNode.mapY]

		hypotenuse = math.sqrt((sides[0]**2)+(sides[1]**2))
		seconds = hypotenuse//2
		# return self.mapX, nextNode.mapX, self.mapY, nextNode.mapY
		for count in range(len(sides)):
			sides[count] = sides[count] * -1
			sides[count] = sides[count] // seconds


		self.mapX += sides[0]
		self.mapY += sides[1]


	# # def fire(self, coOrds, calculated=False):
	# # 	if calculated == False:
	# # 		sides = [self.rect.x-coOrds[0], self.rect.y-coOrds[1]] #calculates the vector
	# # 		hypotenuse = math.sqrt((sides[0]**2)+(sides[1]**2)) #Divides the hypotenuse to work out how many seconds it will take to reach the mouse
	# # 		seconds = hypotenuse/10
	# # 		for count in range(len(sides)):
	# # 			sides[count] = sides[count]*-1
	# # 			sides[count] = sides[count]/seconds #divides the sides by the amount of seconds to work out how much the axis should increment per second
	# # 		self.tell_server("projectile", sides)
	# # 	else:
	# # 		sides = coOrds
	# # 	b = Bullet(self.mapX, self.mapY, sides)
	# # 	bullets.add(b)
	#
	# def rotate(self):
	# 	angle = 0
	# 	if self.direction == "DOWN":
	# 		angle = 180
	# 	elif self.direction == "LEFT":
	# 		angle = 90
	# 	elif self.direction == "RIGHT":
	# 		angle = 270
	#
	#
	# 	self.image = pygame.transform.rotate(self.image_orig,angle)
	#
	# def tell_server(self, action, coOrds =  None):
	# 	if self.connection != None:
	# 		if action == "move":
	# 			packet = {"command":"ENEMY_MOVE","data":{"xPos":self.mapX, "yPos":self.mapY}}
	# 			self.connection.send((json.dumps(packet)+"#").encode())
	# 		elif action == "projectile":
	# 			packet = {"command": "ENEMY_PROJECTILE", "data": {"xPos": self.rect.x+(self.width//2)-2, "yPos":self.rect.y-2, "coOrds":coOrds}}
	# 			self.connection.send((json.dumps(packet) + "#").encode())
	#
	# def move(self):
	# 	keys = pygame.key.get_pressed()
	# 	velocity = 6
	# 	if keys[pygame.K_RIGHT] == True:#Account for diagonal speed
	# 		if keys[pygame.K_UP] == True or keys[pygame.K_DOWN] == True:
	# 			velocity = math.floor(velocity *0.7)
	#
	#
	# 	elif keys[pygame.K_LEFT] == True:
	# 		if keys[pygame.K_UP] == True or keys[pygame.K_DOWN] == True:
	# 			velocity =  math.floor(velocity *0.7)
	#
	#

