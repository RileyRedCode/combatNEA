import pygame, random, time
from game_classes import TILE_SIZE

class NPC(pygame.sprite.Sprite):
	#class variables
	idcount = 0
	directions = {1:"left", 2:"up", 3:"right", 4:"down"}
	def __init__(self, x, y, width, height, image, spkImage, id = False):
		super().__init__()
		#Variables
		self.width = width
		self.height = height
		self.mapX = x
		self.mapY = y
		self.activity = ["idol", pygame.time.get_ticks()]#[activity, time started]
		self.customers = []
		self.dialogue = {}
		self.firstChat = False

		#id
		if id:
			self.id = id
		else:
			self.id = NPC.idcount
		NPC.idcount += 1

		#Assets
		self.image = pygame.image.load(image)
		self.image = pygame.transform.scale(self.image,(self.width,self.height))
		self.rect = self.image.get_rect()
		self.rect.center = -400, -400

		self.speakImage = pygame.image.load(spkImage)
		self.speakImage = pygame.transform.scale(self.speakImage, (800, 800))

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

	def getSpeaker(self):
		if not self.firstChat:
			start = "firstMeet"
		else:
			start = "greetings"
		return self.speakImage, self.dialogue, start

class Monarch(NPC):
	def __init__(self, x, y, id = False):
		super().__init__(x, y, TILE_SIZE, TILE_SIZE, "Assets/NPC.png", "Assets/speaker.png", id)
		#Structure = name:([List of dialogue], [nodes that share edges], type e.g choice)
		self.dialogue = {"firstMeet":(["Can't say I've seen your visage about these parts before..."], ["choice"]),
						 "greetings":(["You again?", "Hello again."], ["choice"]),
						 "choice":(["How may I help you?"],["shopStart", "talk", "end"]),
						 "shopStart":(["Feast your eyes!", "This could all be yours!"], ["choice"]),
						 "end":(["Very well", "Goodbye"], []),
						 "talk":(["We have nothing to talk about"], ["choice"])}

		self.dialogue = constructDialogue(self.dialogue)

class Vertex:
	def __init__(self, name, dialogue):
		self.name = name
		self.dialogue = dialogue
		self.neighbours = []

	def getValue(self):
		return self.dialogue

	def addNeighbour(self, vertex):
		self.neighbours.append(vertex)

	def removeNeighbour(self, vertex):
		if vertex in self.neighbours:
			self.neighbours.remove(vertex)

	def __repr__(self):
		return (f"{self.name}!")

class DialogueGraph:
	def __init__(self):
		self.nodes = []

	def makeEdge(self, vertex1, vertex2):
		vertex1, vertex2 = self.getNode(vertex1), self.getNode(vertex2)
		if vertex1 != "Node could not be found" and vertex2 != "Node could not be found":

				vertex1.addNeighbour(vertex2)

		else:
			print("Node could not be found. Operation failed.")

	def deleteEdge(self, vertex1, vertex2):
		vertex1, vertex2 = self.getNode(vertex1), self.getNode(vertex2)
		if vertex1 != "Node could not be found" and vertex2 != "Node could not be found":

			vertex1.removeNeighbour(vertex2)
			vertex2.removeNeighbour(vertex1)

		else:
			print("Node could not be found. Operation failed.")

	def deleteNode(self, vertex):
		vertex = self.getNode(vertex)
		for value in self.nodes:
			if vertex in value.neighbours:
				value.removeNeighbour(vertex)
		self.nodes.remove(vertex)

	def getNode(self, vertex):
		# Vertex will be the value of the node
		for v in self.nodes:
			if v.name == vertex:
				return v
		return "Node could not be found"

	def makeNode(self, vertex, dialogue):
		self.nodes.append(Vertex(vertex, dialogue))

def constructDialogue(dic):
	d = DialogueGraph()
	#Creating nodes
	for key in dic:
		d.makeNode(key, dic[key][0])
	#Creating Edges
	for key in dic:
		for e in dic[key][1]:
			d.makeEdge(key, e)
	return d

class Button:
	def __init__(self, x, y, beimage, primage):
		self.image = beimage
		self.beimage = beimage
		self.primage = primage
		self.rect = self.image.get_rect()
		self.rect.topleft = (x,y)

	def draw(self,surface):
		surface.blit(self.image,(self.rect.x,self.rect.y))

	def click(self, surface, x, y):
		action = False
		if self.rect.collidepoint((x, y)):
			action = True
			self.image = self.primage
			surface.blit(self.image, (self.rect.x, self.rect.y))
			pygame.display.flip()
			time.sleep(0.15)
			self.image = self.beimage
			surface.blit(self.image, (self.rect.x, self.rect.y))
			pygame.display.flip()
		return action

