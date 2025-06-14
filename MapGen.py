import random, pygame
from PIL import Image

#Need to program linear search to ensure no conflicts slip through, need to guranatee all biomes, DEEP WATER increase likelihood?


#--------------------------- OLD PERIMETER CODE (May want later) ---------------------------------------------------
# perimeter = 2
# for count in range(perimeter):#Horizontal perimeters
#     bMap[count] = ["DWater" for i in range(SCREEN_WIDTH//TILE_SIZE)]
#     bMap[((SCREEN_WIDTH//TILE_SIZE)-1)-count] = ["DWater" for i in range(SCREEN_WIDTH//TILE_SIZE)]
#     bMap[count+perimeter] = ["Water" for i in range(SCREEN_WIDTH//TILE_SIZE)]
#     bMap[((SCREEN_WIDTH // TILE_SIZE) - 1) - (count + perimeter)] = ["Water" for i in range(SCREEN_WIDTH // TILE_SIZE)]
#     for j in range(perimeter):
#         #Left side Dwater overide
#         bMap[count + perimeter][j] = "DWater"
#         bMap[((SCREEN_WIDTH // TILE_SIZE) - 1) - (count + perimeter)][j] = "DWater"
#         #Right side
#         bMap[count + perimeter][((SCREEN_WIDTH//TILE_SIZE)-1)-j] = "DWater"
#         bMap[((SCREEN_WIDTH // TILE_SIZE) - 1) - (count + perimeter)][((SCREEN_WIDTH//TILE_SIZE)-1)-j] = "DWater"
#     for i in range ((SCREEN_WIDTH//TILE_SIZE)-perimeter*4):#excludes the top and bottom perimeters #Vertical perimeters
#         bMap[i+(perimeter*2)][count] = "DWater"
#         bMap[i+(perimeter*2)][((SCREEN_WIDTH//TILE_SIZE)-1)-count] = "DWater"
#         bMap[i+(perimeter*2)][count+perimeter] = "Water"
#         bMap[i+(perimeter*2)][((SCREEN_WIDTH//TILE_SIZE)-1)-(count+perimeter)] = "Water"
#-------------------------------------------------------------------------------------------------------------------------



# biome = {False:(0, 0, 0), "Plains":(0, 255, 0), "Mountain":(170, 170, 170), "HMountain":(255, 255, 255), "Forest":(1, 107, 1), "Water":(0, 0, 255), "DWater":(0, 170, 170)}

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

class MapGenerator:
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
        if not textMap:
            self.textMap = [[False for count in range(self.mapWidth)] for i in range(self.mapWidth)]#Establishes a plain map
        else:
            self.textMap = textMap
        if not obstacles:
            self.obstacles = []
        else:
            self.obstacles = obstacles

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
        return self.textMap

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

    def clearMap(self):
        self.textMap = [[False for count in range(self.mapWidth)] for i in range(self.mapWidth)]

    def text2Tile(self):
        for x in range(self.mapWidth):
            for y in range(self.mapWidth):
                self.textMap[y][x] = Tile(self.textMap[y][x])

    def makeimage(self):
        self.imgMap = Image.new( 'RGB', ((self.mapWidth*TERRAIN_SIZE[0]),(self.mapWidth*TERRAIN_SIZE[0])), "red")
        for x in range(self.mapWidth):
            for y in range(self.mapWidth):
                self.imgMap.paste(self.textMap[y][x].img, (x*TERRAIN_SIZE[0], y*TERRAIN_SIZE[0]))
        self.imgMap.save("map.png")

    def obstacleGen(self):
        for count in range(self.mapWidth//2):
            ranX = random.randint(0, self.mapWidth-1)
            ranY = random.randint(0, self.mapWidth-1)
            while  self.textMap[ranY][ranX] != "Plains":
                ranX = random.randint(0, self.mapWidth - 1)
                ranY = random.randint(0, self.mapWidth - 1)
            ranX = (0*TERRAIN_SIZE[0])+TERRAIN_SIZE[0]//2
            ranY = ranY*TERRAIN_SIZE[0]+TERRAIN_SIZE[0]//2
            self.obstacles.append(["Grave", ranX, ranY])
        return self.obstacles

    def createObstacles(self):
        self.obstacleList = []
        for obstacle in self.obstacles:
            self.obstacleList.append(Obstacle(obstacle[0], obstacle[1], obstacle[2]))

    def finalise(self):
        self.text2Tile()
        self.makeimage()
        self.createObstacles()
        return self.imgMap, self.obstacleList

    # def drawMap(self, screen):
    #     self.blocks = []
    #     screen.fill((255, 0, 0))
    #     rotations = 0
    #     width = 2
    #     length = 0
    #     for count in range(self.mapWidth**2):  # Multiplies width by height to get count
    #         if length == width - 1:
    #             rotations += 1
    #             length = 0
    #         if rotations == 4:
    #             width += 2
    #             rotations = 0
    #         if rotations == 0:  # Top side
    #             cellX = (self.halfWidth) - (width // 2) + length
    #             cellY = (self.halfWidth) - (width // 2)
    #         elif rotations == 1:  # Right side
    #             cellX = (self.halfWidth) + (width // 2) - 1
    #             cellY = (self.halfWidth) - (width // 2) + length
    #         elif rotations == 2:  # Bottom side
    #             cellX = ((self.halfWidth) + (width // 2) - 1) - length
    #             cellY = (self.halfWidth) + (width // 2) - 1
    #         elif rotations == 3:  # Left side
    #             cellX = (self.halfWidth) - (width // 2)
    #             cellY = (((self.halfWidth) + (width // 2)) - 1) - length
    #         length += 1
    #         self.blocks.append(Terrain(cellX, cellY, self))
    #         pygame.display.flip()

class Tile:
    def __init__(self, biome):
        self.biome = biome
        self.img = BIOME_IMGS[biome]

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type, x, y):
        super().__init__()
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.image = pygame.surface.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255, 0, 0))
        pygame.draw.rect(self.image, (255, 0, 0), (0, 0, self.width, self.height))
        self.rect = self.image.get_rect()
        self.mapX = x
        self.mapY = y
        self.rect.center = (x, y)
        self.type = type


#
# oh = MapGenerator()
# oh.generate()
# oh.text2Tile()
# oh.makeimage()


#
#
# def linear_check():
#     for y in range(MAP_WIDTH):
#         for x in range(MAP_WIDTH):
#             if bMap[y][x] == "DWater":
#                 area = 2
#                 for xC in range((x - area), (x + area)):  # This will cycle the 3 cells to the left and the right of the cell aswell as the cell itself
#                     for yC in range(y - area, y + area):
#                         tempX = (xC) % len(bMap)
#                         tempY = (yC) % len(bMap[0])
