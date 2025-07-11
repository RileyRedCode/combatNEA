import pygame, random, socket, threading, json, math
from game_classes import SCREEN_SIZE, TILE_SIZE, obstacleList, enemyList, bullets, characters, explosions, Wall, \
    Character, Bullet, World, Enemy, nodeSetup
from game_classes import WHITE, BLACK


HOST = '127.0.0.1'
PORT = 50000
obstacles = []
textMap = []
MAP = ["00000000000000000000",
       "01111111111111111110",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "010000000C0000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000000000000000010",
       "01000111111111111110",
       "00000000000000000000"]
Waiting = True
def recv_from_server(conn):
    global Waiting
    while True:
        data = conn.recv(1024)
        if data:

            packet = data.decode()
            packet = packet.split("#")[0]
            print(packet)
            try:
                packet = json.loads(packet)

            except:#continue prevents the code from trying to continue analysing this packet
                continue

            if packet["command"] == "START":
                Waiting = False

            if packet["command"] == "SETUP":
                c = Character(int(packet["data"]["PlayerX"]), int(packet["data"]["PlayerY"]), conn)
                characters.add(c)
                playerTwo = Character(int(packet["data"]["EnemyX"]), int(packet["data"]["EnemyY"]))
                characters.add(playerTwo)

            if packet["command"] == "MAP":
                textMap.append(packet["data"]["List"])

            if packet["command"] == "OBSTACLES":
                for ob in packet["data"]:
                    obstacles.append(ob)

            if packet["command"] == "ENEMIES":
                for i in packet["data"]:
                    enemyList.add(Enemy(*i))

            if packet["command"] == "MOVE":
                playerTwo.mapX = packet["data"]["xPos"]
                playerTwo.mapY = packet["data"]["yPos"]

            if packet["command"] == "PROJECTILE":
                playerTwo.fire(packet["data"]["coOrds"], True)

            if packet["command"] == "ENEMYACTIONS":
                for command in packet["data"]:
                    for enemy in enemyList:
                        if enemy.id == command["id"]:
                            if not enemy.startTime:
                                if command["action"] == "MOVE":
                                    enemy.mapX, enemy.mapY = command["x"], command["y"]

                                elif command["action"] == "ATTACK":
                                    enemy.startTime = pygame.time.get_ticks()

                                elif command["action"] == "DIE":
                                    enemy.attack()


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((HOST,PORT))
threading.Thread(target=recv_from_server, args=(s,)).start()

pygame.display.init()
pygame.font.init()
SCREEN = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

def wait_screen():
    global Waiting
    text = "Waiting for the other player to connect"
    f = pygame.font.SysFont("Arial",24)
    output = f.render(text,True, BLACK)
    running = True
    while Waiting:
        SCREEN.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                Waiting = False
        SCREEN.blit(output,(200,400))
        pygame.display.update()
    return running

textMap = [['DWater', 'Plains', 'Plains', 'Plains', 'Water', 'DWater', 'Plains', 'Plains', 'Forest', 'Forest', 'Forest', 'Plains', 'Forest', 'Forest', 'Plains', 'Forest', 'Forest', 'Plains', 'Forest', 'Mountain'], ['Forest', 'Water', 'Forest', 'Plains', 'Plains', 'Plains', 'Water', 'Water', 'Water', 'Forest', 'Water', 'Plains', 'Plains', 'Forest', 'Plains', 'Forest', 'Plains', 'Plains', 'Forest', 'Forest'], ['Forest', 'Plains', 'Forest', 'Water', 'Plains', 'Forest', 'Plains', 'Forest', 'Forest', 'Plains', 'Plains', 'Mountain', 'Plains', 'Plains', 'Plains', 'Forest', 'Plains', 'Forest', 'Plains', 'Forest'], ['Forest', 'Plains', 'Water', 'Forest', 'Plains', 'Plains', 'Plains', 'Forest', 'Forest', 'Forest', 'Forest', 'Plains', 'Plains', 'Plains', 'Plains', 'Forest', 'Forest', 'Plains', 'Forest', 'Mountain'], ['Forest', 'Plains', 'Plains', 'Plains', 'Forest', 'Forest', 'Forest', 'Plains', 'Forest', 'Mountain', 'Plains', 'Plains', 'Plains', 'Plains', 'Water', 'Plains', 'Forest', 'HMountain', 'Plains', 'Forest'], ['Forest', 'Plains', 'Forest', 'Forest', 'Water', 'Forest', 'Plains', 'Plains', 'Plains', 'Plains', 'Plains', 'Plains', 'Plains', 'Water', 'Forest', 'Forest', 'HMountain', 'Forest', 'Mountain', 'HMountain'], ['Forest', 'Mountain', 'Forest', 'Plains', 'Plains', 'Plains', 'Forest', 'Mountain', 'Water', 'Plains', 'Forest', 'Forest', 'Plains', 'Mountain', 'Forest', 'Forest', 'Forest', 'Mountain', 'Forest', 'Forest'], ['Plains', 'Plains', 'Water', 'Forest', 'Mountain', 'Plains', 'Plains', 'Plains', 'Water', 'Forest', 'DWater', 'Forest', 'DWater', 'Mountain', 'Plains', 'Mountain', 'Mountain', 'Forest', 'Forest', 'Forest'], ['Mountain', 'Forest', 'Forest', 'Plains', 'Plains', 'Plains', 'Forest', 'Mountain', 'Forest', 'Water', 'Water', 'Mountain', 'Mountain', 'Forest', 'HMountain', 'Mountain', 'Mountain', 'Plains', 'Plains', 'Forest'], ['Water', 'Forest', 'Forest', 'Plains', 'Plains', 'Forest', 'Mountain', 'Water', 'Plains', 'DWater', 'DWater', 'Mountain', 'Water', 'Mountain', 'Forest', 'Forest', 'Forest', 'Plains', 'Forest', 'Mountain'], ['Plains', 'Plains', 'Plains', 'Plains', 'Plains', 'Plains', 'Forest', 'Water', 'Mountain', 'HMountain', 'HMountain', 'Mountain', 'Water', 'Forest', 'Plains', 'Plains', 'Forest', 'Mountain', 'Forest', 'Forest'], ['Forest', 'Forest', 'Mountain', 'Forest', 'Plains', 'Water', 'Forest', 'Water', 'Mountain', 'Forest', 'Water', 'DWater', 'Water', 'Mountain', 'HMountain', 'HMountain', 'Mountain', 'Mountain', 'Mountain', 'Forest'], ['Plains', 'Plains', 'Plains', 'Water', 'Forest', 'Forest', 'Forest', 'Forest', 'HMountain', 'HMountain', 'Mountain', 'Mountain', 'Water', 'Forest', 'Mountain', 'Plains', 'Mountain', 'Mountain', 'Mountain', 'Mountain'], ['Plains', 'Plains', 'Plains', 'Forest', 'Plains', 'Plains', 'Water', 'Plains', 'Forest', 'Mountain', 'DWater', 'DWater', 'HMountain', 'Mountain', 'Forest', 'Forest', 'Forest', 'Forest', 'Plains', 'Plains'], ['Plains', 'Plains', 'Plains', 'Water', 'Plains', 'Plains', 'Mountain', 'Forest', 'Plains', 'Plains', 'Water', 'Forest', 'Mountain', 'Mountain', 'DWater', 'Plains', 'Forest', 'Forest', 'Forest', 'Forest'], ['Plains', 'Forest', 'Forest', 'Plains', 'Plains', 'Plains', 'Forest', 'Forest', 'Water', 'Mountain', 'Plains', 'Forest', 'Plains', 'Mountain', 'Plains', 'Plains', 'Mountain', 'Forest', 'Forest', 'Plains'], ['Forest', 'Forest', 'Plains', 'Forest', 'Plains', 'Forest', 'Forest', 'Forest', 'Forest', 'Forest', 'Plains', 'Mountain', 'Plains', 'Plains', 'Forest', 'Forest', 'Forest', 'Plains', 'Forest', 'Plains'], ['Plains', 'Mountain', 'Forest', 'Plains', 'Plains', 'Plains', 'Mountain', 'Plains', 'Mountain', 'Forest', 'Forest', 'Forest', 'Mountain', 'Forest', 'Plains', 'Water', 'Forest', 'Mountain', 'Forest', 'Plains'], ['Plains', 'Plains', 'Plains', 'Forest', 'Mountain', 'Mountain', 'Forest', 'Forest', 'Forest', 'Forest', 'Forest', 'Plains', 'Plains', 'Forest', 'Forest', 'Water', 'Plains', 'Plains', 'Forest', 'Plains'], ['Plains', 'Forest', 'Forest', 'Forest', 'Forest', 'Plains', 'Plains', 'Forest', 'Plains', 'Plains', 'Forest', 'Forest', 'Mountain', 'Forest', 'Plains', 'Forest', 'Plains', 'Water', 'Forest', 'Mountain']]

y = 0
for row in MAP:
    x = 0
    for cell in row:
        if cell == "1":
            w = Wall((x*TILE_SIZE)+TILE_SIZE//2,(y*TILE_SIZE)+TILE_SIZE//2)
            obstacleList.add(w)
        x += 1
    y+=1

running = wait_screen()

# enemyList.add(Enemy(900, 900))
# enemyList.add(Enemy(1000, 1100))
# enemyList.add(Enemy(2000, 900))
# enemyList.add(Enemy(900, 800))
# enemyList.add(Enemy(900, 6000))

world = World(textMap, obstacles)
for obstacle in world.obstacleList:
    obstacleList.add(obstacle)
world.nodes = nodeSetup(obstacleList, world.nodes)
count = 0


# for count in range(10):
# 	ranY = random.randint(0,len(world.nodes)-1)
# 	ranX = random.randint(0,len(world.nodes[0])-1)
# 	while not world.nodes[ranY][ranX]:
# 		ranY = random.randint(0,len(world.nodes)-1)
# 		ranX = random.randint(0,len(world.nodes[0])-1)
#
# 	print(world.nodes[ranY][ranX].neighbours)
	# print(world.nodes[19][5].neighbours, "\n", world.nodes[19][5].topLeft, world.nodes[19][5].up,
	# 	  world.nodes[19][5].topRight,
	# 	  world.nodes[19][5].right, world.nodes[19][5].bottomRight, world.nodes[19][5].down,
	# 	  world.nodes[19][5].bottomLeft, world.nodes[19][5].left)

#
# for y in world.nodes:
# 	string = ""
# 	for x in y:
# 		if x:
# 			string += "0"
# 		else:
# 			string += "1"
# 	print(string)

player = characters.sprites()[0]
spotting = False
while running == True:
    SCREEN.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
        if event.type == pygame.MOUSEBUTTONUP:
            if not pygame.mouse.get_pressed()[0] and event.button == 1:
                coOrds = pygame.mouse.get_pos()
                player.fire(coOrds)

    bullets.update()
    explosions.update()
    player.move()
    player.camera.worldAdjust(SCREEN, world, characters, enemyList)
    player.camera.reAdjust()
    player.camera.bulletAdjust(bullets, explosions)
    player.camera.obstacleAdjust(obstacleList)
    for enemy in enemyList:
        # If enough time has passed
        if pygame.time.get_ticks() - enemy.startTime >= 200 and enemy.startTime:
            enemy.attack()
        # if not enemy.startTime:
        #     path = enemy.locate([player], world)
        #     enemy.travel(path)
        # else:
        #     enemy.attack()
        # # print(enemy.mapX, enemy.mapY)

    world.draw(SCREEN)
    explosions.draw(SCREEN)
    enemyList.draw(SCREEN)
    characters.draw(SCREEN)
    obstacleList.draw(SCREEN)
    bullets.draw(SCREEN)
    player.hud.draw(SCREEN)
    clock.tick(60)
    pygame.display.update()