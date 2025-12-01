import random, pygame, math
from xml.etree.ElementTree import XMLParser
from npcs import Monarch
from PIL import Image


# pygame.display.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
TILE_SIZE = SCREEN_WIDTH//20
TERRAIN_SIZE = (800, 800)
MAP_WIDTH = 20

BIOME_IMGS = {"Plains":Image.new("RGB", (TERRAIN_SIZE), (0, 255, 0)),
                "Mountain":Image.new("RGB", (TERRAIN_SIZE), (170, 170, 170)),
                "HMountain":Image.new("RGB", (TERRAIN_SIZE), (255, 255, 255)),
                "Forest":Image.new("RGB", (TERRAIN_SIZE), (1, 107, 1)),
                "Water":Image.new("RGB", (TERRAIN_SIZE), (0, 0, 255)),
                "DWater":Image.new("RGB", (TERRAIN_SIZE), (0, 170, 170))}

'''
Name: MapGenerator
Purpose: Used to generate maps, create map images and generate objects.
'''
class MapGenerator:

    '''
    Name: __init__
    Parameters: textMap:list, obstacles:list
    Returns: None
    Purpose: Constructor
    '''
    def __init__(self, textMap=False, obstacles = False):
        self.mapWidth = 20
        self.halfWidth = self.mapWidth // 2
        self.biomes = ["Plains", "Mountain", "HMountain", "Forest", "Water", "DWater"]#List of all biomes possible
        #Probabilities that are tied to each terrain
        self.probability = {False:{"Plains":10, "Mountain":6, "HMountain":2, "Forest":8, "Water":6, "DWater":4, False:0},
              "Plains":{"Plains":25, "Mountain":0, "HMountain":0, "Forest":15, "Water":5, "DWater":0, False:0},
              "Mountain":{"Plains":0, "Mountain":20, "HMountain":15, "Forest":15, "Water":0, "DWater":0, False:0},
              "HMountain":{"Plains":0, "Mountain":35, "HMountain":15, "Forest":0, "Water":0, "DWater":0, False:0},
              "Forest":{"Plains":15, "Mountain":18, "HMountain":0, "Forest":25, "Water":0, "DWater":0, False:0},
              "Water":{"Plains":15, "Mountain":0, "HMountain":0, "Forest":0, "Water":15, "DWater":10, False:0},
              "DWater":{"Plains":0, "Mountain":0, "HMountain":0, "Forest":0, "Water":30, "DWater":15, False:0}}
        #Influences
        self.conflictions = {False:{"Plains":0, "Mountain":0, "HMountain":0, "Forest":0, "Water":0, "DWater":0, False:0},
                      "Plains":{"Plains":0, "Mountain":1, "HMountain":1, "Forest":0, "Water":0, "DWater":1, False:0},
                      "Mountain":{"Plains":1, "Mountain":0, "HMountain":0, "Forest":0, "Water":1, "DWater":1, False:0},
                      "HMountain":{"Plains":1, "Mountain":0, "HMountain":0, "Forest":1, "Water":1, "DWater":1, False:0},
                      "Forest":{"Plains":0, "Mountain":0, "HMountain":1, "Forest":0, "Water":1, "DWater":1, False:0},
                      "Water":{"Plains":0, "Mountain":1, "HMountain":1, "Forest":1, "Water":0, "DWater":0, False:0},
                      "DWater":{"Plains":1, "Mountain":1, "HMountain":1, "Forest":1, "Water":0, "DWater":0, False:0}}
        self.NPCs = pygame.sprite.Group()
        if not textMap:
            self.textMap = [[False for count in range(self.mapWidth)] for i in range(self.mapWidth)]#Establishes a plain map
        else:
            self.textMap = textMap
        if not obstacles:
            self.obstacles = []
        else:
            self.obstacles = obstacles

        '''
    	Name: generate
    	Parameters: None
    	Returns: self.textMap:list, self.obstacles:list, self.NPCs:sprite group
    	Purpose: This generates a map using soft constraint satisfaction and then generates obstacles. Constraint satisfaction 
    	involves finding the tile that creates the least conflicts in order to generate a somewhat natural map while still 
    	being random. This works by selecting random tiles in order to (prevent artifacting) and then choosing a random terrain 
    	which is influenced by the probabilities of surropunding tiles.  
    	'''
    def generate(self):#Generates a map
        success = False
        while not success:
            # This checks the cells of the map in a spiral fashion
            rotations = 0
            width = 2
            length = 0
            for count in range(self.mapWidth ** 2):  # Multiplies width by height to get count
                if length == width - 1:
                    rotations += 1
                    length = 0
                if rotations == 4:
                    width += 2
                    rotations = 0
                if rotations == 0:  # Top side
                    cellX = (self.halfWidth) - (width // 2) + length
                    cellY = (self.halfWidth) - (width // 2)
                elif rotations == 1:  # Right side
                    cellX = (self.halfWidth) + (width // 2) - 1
                    cellY = (self.halfWidth) - (width // 2) + length
                elif rotations == 2:  # Bottom side
                    cellX = ((self.halfWidth) + (width // 2) - 1) - length
                    cellY = (self.halfWidth) + (width // 2) - 1
                elif rotations == 3:  # Left side
                    cellX = (self.halfWidth) - (width // 2)
                    cellY = (((self.halfWidth) + (width // 2)) - 1) - length
                length += 1

                probs = self.checkProbability(cellX, cellY)[0]
                if self.textMap[cellY][cellX] == False:  # If the cell is undefined
                    bestType = False
                    leastConflicts = 99

                    # This creates a list of ranges for each probability
                    pool = 0
                    probabilities = []
                    count = 0
                    stagger = 0
                    for key in probs:
                        if count != 0:
                            pool += probs[key]
                            probabilities.append([stagger, stagger + probs[key]])
                        stagger += probs[key]
                        count += 1

                    for count in range(2):
                        num = random.randint(0, pool - 1)# gens a random number in the range of all probabilities combined
                        # Selects the biome which the random number is in range of
                        found = False
                        count = 0
                        while not found:
                            if num in range(probabilities[count][0], probabilities[count][1]):
                                found = True
                                tTerrain = self.biomes[count]
                            count += 1

                        self.textMap[cellY][cellX] = tTerrain
                        conflicts = self.checkProbability(cellX, cellY)[1]
                        if conflicts < leastConflicts:# if the terrain is more likely than the current most likely
                            leastConflicts = conflicts
                            bestType = tTerrain
                    self.textMap[cellY][cellX] = bestType
            success = self.biomeCheck()
            if not success:#Clears map so that the algorithm can retry
                self.clearMap()
        self.obstacleGen()
        return self.textMap, self.obstacles, self.NPCs

    '''
    Name: checkProbability
    Parameters: x:int, y:int
    Returns: probs:dictionary, conflicts:int
    Purpose: This function will calculate the probabilities using the surrounding tiles to the attached tile and calculate how many conflicts are generated.
    '''
    def checkProbability(self, x, y):#Gets a pool of probabilities
        area = 3
        conflicts = 0
        probs = {False:0, "Plains":0, "Mountain":0, "HMountain":0, "Forest":0, "Water":0, "DWater":0}#Dictionary of probability for each terrain based of surrounding terrain
        for xC in range((x - area), (x + area)):#This will cycle the 3 cells to the left and the right of the cell aswell as the cell itself
            for yC in range(y - area, y + area):
                tempX = xC%self.mapWidth
                tempY = yC%self.mapWidth
                conflicts += self.conflictions[self.textMap[y][x]][self.textMap[tempY][tempX]]
                for key in self.probability:
                    probs[key] += self.probability[self.textMap[tempX][tempY]][key]#Adds the probabilities from this cell
        return probs, conflicts

    '''
    Name: biomeCheck
    Parameters: None
    Returns: safe:boolean
    Purpose: Ensures that there is at least a certain amount of each type of tile.
    '''
    def biomeCheck(self):
        biomeCount = {"Plains": 0, "Mountain": 0, "HMountain": 0,
                      "Forest": 0, "Water": 0, "DWater": 0}
        for y in self.textMap:
            for x in y:
                for bi in biomeCount:
                    if bi == x:
                        biomeCount[bi] += 1
        safe = True
        for bi in biomeCount:
            if biomeCount[bi] < 7:
                safe  = False
        return safe

    '''
    Name: clearMap
    Parameters: None
    Returns: None
    Purpose: This clears the map and will only be called if a map is unsatisfactory. 
    '''
    def clearMap(self):
        self.textMap = [[False for count in range(self.mapWidth)] for i in range(self.mapWidth)]

    '''
    Name: text2Tile
    Parameters: None
    Returns: None
    Purpose: This creates Tiles for each terrain in the maps.
    '''
    def text2Tile(self):
        for x in range(self.mapWidth):
            for y in range(self.mapWidth):
                self.textMap[y][x] = Tile(self.textMap[y][x])

    '''
    Name: makeimage
    Parameters: None
    Returns: None
    Purpose: This creates an image of the map.
    '''
    def makeimage(self):
        self.imgMap = Image.new( 'RGB', ((self.mapWidth*TERRAIN_SIZE[0]),(self.mapWidth*TERRAIN_SIZE[0])), "red")
        for x in range(self.mapWidth):
            for y in range(self.mapWidth):
                self.imgMap.paste(self.textMap[y][x].img, (x*TERRAIN_SIZE[0], y*TERRAIN_SIZE[0]))
        self.imgMap.save("map.png")

    '''
    Name: obstacleGen
    Parameters: None
    Returns: self.obstacles:list
    Purpose: This generates obstacles and also instantiates NPCs for any houses.
    '''
    def obstacleGen(self):
        used = []
        c = 0
        for count in range(3):
            x = random.randint(0, self.mapWidth-1)
            y = random.randint(0, self.mapWidth-1)
            while self.textMap[y][x] == "DWater" or self.textMap[y][x] == "Water" or (x, y) in used:
                x = random.randint(0, self.mapWidth - 1)
                y = random.randint(0, self.mapWidth - 1)
            self.NPCs.add(Monarch((x * TERRAIN_SIZE[0]) + (TILE_SIZE * 8),
                                  (y * TERRAIN_SIZE[1]) + (TILE_SIZE * 8)))
            self.obstacles.append((((x * TERRAIN_SIZE[0]), (y * TERRAIN_SIZE[1]), self.NPCs.sprites()[c].id), "House"))
            c += 1
            used.append((x, y))
        for count in range(self.mapWidth//2):
            ranX = random.randint(0, self.mapWidth-1)
            ranY = random.randint(0, self.mapWidth-1)
            while  self.textMap[ranY][ranX] != "Plains" or (ranX, ranY) in used:
                ranX = random.randint(0, self.mapWidth - 1)
                ranY = random.randint(0, self.mapWidth - 1)
            used.append((ranX, ranY))
            ranX = ranX*TERRAIN_SIZE[0]+TERRAIN_SIZE[0]//2
            ranY = ranY*TERRAIN_SIZE[0]+TERRAIN_SIZE[0]//2
            self.obstacles.append(((ranX, ranY), "Grave"))

        for count in range(self.mapWidth//2):
            ranX = random.randint(0, self.mapWidth-1)
            ranY = random.randint(0, self.mapWidth-1)
            while  self.textMap[ranY][ranX] != "Forest" or (ranX, ranY) in used:
                ranX = random.randint(0, self.mapWidth - 1)
                ranY = random.randint(0, self.mapWidth - 1)
            num = random.randint(1,2)
            for count in range(0, num):
                ranXo = ranX*TERRAIN_SIZE[0]+((TERRAIN_SIZE[0]//3) * random.randint(1,2))
                ranYo = ranY*TERRAIN_SIZE[0]+((TERRAIN_SIZE[0]//3) * random.randint(1,2))
                self.obstacles.append(((ranXo, ranYo), "Bush"))
        return self.obstacles

    '''
    Name: createObstacles
    Parameters: None
    Returns: None
    Purpose: Instantiates buildings for each obstacle in obstacles.
    '''
    def createObstacles(self):
        self.obstacleList = pygame.sprite.Group()
        for obstacle in self.obstacles:
            if obstacle[1] == "House":
                self.obstacleList.add(House(*obstacle[0]))
            elif obstacle[1] == "Grave":
                self.obstacleList.add(Grave(*obstacle[0]))
            elif obstacle[1] == "Bush":
                self.obstacleList.add(Bush(*obstacle[0]))

    '''
    Name: finalise
    Parameters: None
    Returns: imgMap:image, obstacleList:sprite group
    Purpose: Carries out all the steps needed after the initial map creation to finish it.
    '''
    def finalise(self):
        self.text2Tile()
        self.makeimage()
        self.createObstacles()
        return self.imgMap, self.obstacleList

'''
Name: Tile
Purpose: Stores the image of a relevant terrain.
'''
class Tile:

    '''
    Name: __init__
    Parameters: biome:string
    Returns: None
    Purpose: Constructor
    '''
    def __init__(self, biome):
        self.biome = biome
        self.img = BIOME_IMGS[biome]


'''
Name: Obstacle
Purpose: This is a parent class used for obstacles which are objects the player and enemies cannot pass through.
'''
class Obstacle(pygame.sprite.Sprite):

    '''
    Name: __init__
    Parameters: x:int, y:int, width:int, height:int, image:string, name:string
    Returns: None
    Purpose: Constructor
    '''
    def __init__(self, x, y, width, height, image, name):
        super().__init__()
        self.type = name
        self.mapX = x
        self.mapY = y
        self.width = width
        self.height = height
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    '''
    Name: __repr__
    Parameters: None
    Returns: string
    Purpose: Used for debug to check obstacle positions are valid.
    '''
    def __repr__(self):
        return f"{self.mapX}, {self.mapY}, obstacle"


'''
Name: House
Purpose: A large obstacle owned by an NPC
'''
class House(Obstacle):

    '''
    Name: __init__
    Parameters: x:int, y:int, owner:object
    Returns: None
    Purpose: Constructor
    '''
    def __init__(self, x, y, owner):
        super().__init__(x + TILE_SIZE*4, y + TILE_SIZE*4, TILE_SIZE*8, TILE_SIZE*8, "Assets/house.png", "House")
        self.owner = owner


'''
Name: Grave
Purpose: Special type of obstacle which spawns enemies if a player is too close
'''
class Grave(Obstacle):

    '''
    Name: __init__
    Parameters: x:int, y:int
    Returns: None
    Purpose: Constructor
    '''
    def __init__(self, x, y):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE, "Assets/skull.png", "Grave")
        self.lastSpawn = pygame.time.get_ticks()

    def checkSpawn(self, playerPos):
        close = False
        for pos in playerPos:
            hypotenuse = math.sqrt(((pos[0] - self.mapX)**2) + ((pos[1] - self.mapY)**2))
            if hypotenuse < 600:
                close = True
        if close:
            if pygame.time.get_ticks() - self.lastSpawn > 2000:
                self.lastSpawn = pygame.time.get_ticks()
                return self.mapX + TILE_SIZE + (TILE_SIZE//2), self.mapY +TILE_SIZE+ (TILE_SIZE//2)
        return False


'''
Name: Bush
Purpose: Generic obstacle.
'''
class Bush(Obstacle):

    '''
    Name: __init__
    Parameters: x:int, y:int
    Returns: None
    Purpose: Constructor
    '''
    def __init__(self, x, y):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE, "Assets/bush.png", "Bush")


