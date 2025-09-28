import pygame, random, time

TILE_SIZE = 40

'''
Name: NPC
Purpose: Can be talked to and will sell goods to the player. 
'''
class NPC(pygame.sprite.Sprite):
	#class variables
	idcount = 0
	directions = {1:"left", 2:"up", 3:"right", 4:"down"}
	'''
	Name: __init__
	Parameters: x:int, y:int, width:int, height:int, image:string, spkImage:string, id:int
	Returns: None
	Purpose: Constructor
	'''
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

	'''
	Name: determineState
	Parameters: None
	Returns: self.id:int, self.mapX:int, self.mapY:int
	Purpose: Will swap states if enough time has passed and it is not talking then return it's position.
	'''
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

	'''
	Name: addCustomer
	Parameters: customer:int
	Returns: None
	Purpose: Adds customer to the list of customers and updates the activity state.
	'''
	def addCustomer(self, customer):
		self.customers.append(customer)
		if self.activity[0] != "talking":
			self.activity[0] = "talking"

	'''
	Name: removeCustomer
	Parameters: customer:int
	Returns: None
	Purpose: Removes the specfied customer to the list of customers and updates the activity state.
	'''
	def removeCustomer(self, customer):
		self.customers.remove(customer)
		if len(self.customers) == 0:
			self.activity[0] = "idol"

	'''
	Name: getSpeaker
	Parameters: None
	Returns: self.speakImage:image, self.object, start:string
	Purpose: Returns the speakers image aswell as which dialogue node should be started from depending on wether the player has spoke to them before.
	'''
	def getSpeaker(self):
		if not self.firstChat:
			start = "firstMeet"
		else:
			start = "greetings"
		return self.speakImage, self.dialogue, start

'''
Name: Monarch
Purpose: This is a variant of the NPC using inheritance
'''
class Monarch(NPC):

	'''
	Name: __init__
	Parameters: x:int, y:int, id:int
	Returns: None
	Purpose: Constructor
	'''
	def __init__(self, x, y, id = False):
		super().__init__(x, y, TILE_SIZE, TILE_SIZE, "Assets/NPC.png", "Assets/speaker.png", id)
		#Structure = name:([List of dialogue], [nodes that share edges], type e.g choice)
		self.dialogue = {"firstMeet":(["Can't say I've seen your visage about these parts before..."], ["choice"]),
						 "greetings":(["You again?", "Hello again."], ["choice"]),
						 "choice":(["How may I help you?"],["shopStart", "talk", "end"]),
						 "shopStart":(["Feast your eyes!", "This could all be yours!"], ["choice"], "Shop"),
						 "end":(["Very well", "Farewell"], [], "Goodbye"),
						 "talk":(["We have nothing to talk about"], ["choice"], "Chat")}

		self.dialogue = constructDialogue(self.dialogue)

'''
Name: Vertex
Purpose: Stores a singular piece of dialogue it's neighbours and any conditions. Designined to be a node in a dialogue Graph
'''
class Vertex:
	'''
	Name: __init__
	Parameters: name:string, dialogue:string, option:string
	Returns: None
	Purpose: Constructor
	'''
	def __init__(self, name, dialogue, option = False):
		self.name = name
		self.dialogue = dialogue
		self.neighbours = []
		self.option = option
		self.condition = False

	'''
	Name: getValue
	Parameters: None
	Returns: self.dialogue:string
	Purpose: Returns the dialogue string stored in the vertex.
	'''
	def getValue(self):
		return self.dialogue

	'''
	Name: addNeighbour
	Parameters: vertex:object
	Returns: None
	Purpose: Adds a vertex to the neighbours list.
	'''
	def addNeighbour(self, vertex):
		self.neighbours.append(vertex)

	'''
	Name: removeNeighbour
	Parameters: vertex:object
	Returns: None
	Purpose: Removes the neighbour given from the neighbours list if it is present.
	'''
	def removeNeighbour(self, vertex):
		if vertex in self.neighbours:
			self.neighbours.remove(vertex)

	'''
	Name: __repr__
	Parameters: None
	Returns: string
	Purpose: Used for debugging and checking that a dialogue graph has been constructed correctly.
	'''
	def __repr__(self):
		return (f"{self.name}!")

'''
Name: DialogueGraph
Purpose: This is an important data structure used to store an NPC's dialogue. Each node stores its neighbours allowing for a clear traversal during a conversation.
'''
class DialogueGraph:

	'''
	Name: __init__
	Parameters: None
	Returns: None
	Purpose: Constructor
	'''
	def __init__(self):
		self.nodes = []

	'''
	Name: makeEdge
	Parameters: vertex1:string, vertex2:string
	Returns: None
	Purpose: Adds a neighbour to the relevant node.
	'''
	def makeEdge(self, vertex1, vertex2):
		vertex1, vertex2 = self.getNode(vertex1), self.getNode(vertex2)
		if vertex1 != "Node could not be found" and vertex2 != "Node could not be found":

				vertex1.addNeighbour(vertex2)

		else:
			print("Node could not be found. Operation failed.")

	'''
	Name: deleteEdge
	Parameters: vertex1:string, vertex2:string
	Returns: None
	Purpose: Removes a neighbour from the relevant node.
	'''
	def deleteEdge(self, vertex1, vertex2):
		vertex1, vertex2 = self.getNode(vertex1), self.getNode(vertex2)
		if vertex1 != "Node could not be found" and vertex2 != "Node could not be found":

			vertex1.removeNeighbour(vertex2)
			vertex2.removeNeighbour(vertex1)

		else:
			print("Node could not be found. Operation failed.")

	'''
	Name: deleteNode
	Parameters: vertex:string
	Returns: None
	Purpose: Removes all edges fron a Node before deleting it.
	'''
	def deleteNode(self, vertex):
		vertex = self.getNode(vertex)
		for value in self.nodes:
			if vertex in value.neighbours:
				value.removeNeighbour(vertex)
		self.nodes.remove(vertex)

	'''
	Name: getNode
	Parameters: vertex:string
	Returns: None
	Purpose: Returns the relevant node if it could be found.
	'''
	def getNode(self, vertex):
		# Vertex will be the value of the node
		for v in self.nodes:
			if v.name == vertex:
				return v
		return "Node could not be found"

	'''
	Name: makeNode
	Parameters: vertex:string, dialogue:string, option:string
	Returns: None
	Purpose: Instantiates a vertex class and appends it to the nodes list.
	'''
	def makeNode(self, vertex, dialogue, option = False):
		self.nodes.append(Vertex(vertex, dialogue, option))


'''
Name: constructDialogue
Parameters: dic:dictionary
Returns: d:object
Purpose: Creates a dictionary then converts every single key in the dictionary into a vertex. It then establishes edges between any relevant nodes. 
'''
def constructDialogue(dic):
	d = DialogueGraph()
	#Creating nodes
	for key in dic:
		option = False
		if len(dic[key]) == 3:
			option = dic[key][2]
		d.makeNode(key, dic[key][0], option)
	#Creating Edges
	for key in dic:
		for e in dic[key][1]:
			d.makeEdge(key, e)
	return d
