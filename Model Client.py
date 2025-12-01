import pygame, random, socket, threading, json, math
from game_classes import SCREEN_SIZE, obstacleList, npcList, enemyList, bullets, characters, explosions, Wall, \
    Character, Bullet, World, Enemy, nodeSetup, TILE_SIZE, Pistol, Shotgun, NeoGun, NeoShotgun
from game_classes import WHITE, BLACK
from npcs import Monarch

HOST = '127.0.0.1'
PORT = 50000
obstacles = []
textMap = []

Waiting = True

'''
Name: recv_from_server
Parameters: conn:connection
Returns: None
Purpose: Recieves messages from the server and responds as appropriate.
'''

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
                c = Character(int(packet["data"]["PlayerX"]), int(packet["data"]["PlayerY"]), conn, False, packet["data"]["id"])
                characters.add(c)
                if packet["data"]["id"] == 1:
                    otherId = 0
                else:
                    otherId = 1
                playerTwo = Character(int(packet["data"]["EnemyX"]), int(packet["data"]["EnemyY"]), None, False, otherId)
                characters.add(playerTwo)

            if packet["command"] == "MAP":
                textMap.append(packet["data"]["List"])

            if packet["command"] == "OBSTACLES":
                for ob in packet["data"]:
                    obstacles.append(ob)

            if packet["command"] == "NPCS":
                for i in packet["data"]:
                    npcList.add(Monarch(*i))

            if packet["command"] == "TALK":
                for npc in npcList:
                    if npc.id == packet["data"]["id"]:
                        player.talking = npc
                        player.hud.startAnimation("open", player.talking)
                        npc.addCustomer(player.id)
                        if not npc.firstChat:
                            npc.firstChat = True


            if packet["command"] == "ENEMIES":
                for i in packet["data"]:
                    enemyList.add(Enemy(*i))

            if packet["command"] == "MOVE":
                playerTwo.mapX = packet["data"]["xPos"]
                playerTwo.mapY = packet["data"]["yPos"]

            if packet["command"] == "WEAPONSWAP":
                if packet["data"]["weapon"] == "Pistol":
                    playerTwo.activeWeapon = Pistol(playerTwo)
                elif packet["data"]["weapon"] == "Shotgun":
                    playerTwo.activeWeapon = Shotgun(playerTwo)
                elif packet["data"]["weapon"] == "NeoGun":
                    playerTwo.activeWeapon = NeoGun(playerTwo)
                elif packet["data"]["weapon"] == "NeoShotgun":
                    playerTwo.activeWeapon = NeoShotgun(playerTwo)

            if packet["command"] == "PROJECTILE":
                playerTwo.fire((packet["data"]["start"], packet["data"]["bulletList"], packet["data"]["angle"]))

            if packet["command"] == "ENEMYDAMAGE":
                for enemy in enemyList:
                    if enemy.id == packet["data"]["id"]:
                        enemy.takeDamage(packet["data"]["amount"])

            if packet["command"] == "EXPLOSIONDAMAGE":
                player.takeDamage(packet["data"])

            if packet["command"] == "DIE":
                if player.id == packet["data"]:
                    player.tell_server("death")
                    player.die()
                else:
                    for p in characters:
                        if p.id == packet["data"]:
                            p.deadSprite()
                            p.dead = True

            if packet["command"] == "REVIVAL":
                for p in characters:
                    if p.id in packet["data"]["idList"]:
                        p.reviveSelf()
                        if p == player:
                            player.tell_server("revived")

            if packet["command"] == "NPCACTIONS":
                for command in packet["data"]:
                    for npc in npcList:
                        if npc.id == command["id"]:
                            npc.mapX = command["x"]
                            npc.mapY = command["y"]

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
                                    player.tell_server("kill", command["id"])


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((HOST,PORT))
threading.Thread(target=recv_from_server, args=(s,)).start()

pygame.display.init()
pygame.font.init()
SCREEN = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

'''
Name: wait_screen
Parameters: None
Returns: None
Purpose: Will display a waiting screen until it has recieved a mesage to stop from the server.
'''
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

running = wait_screen()

world = World(textMap, obstacles)
world.nodes = nodeSetup(world.obstacleList, world.nodes)
count = 0

player = characters.sprites()[0]
for p in characters:
    p.inventory.append(Shotgun(p))
    p.inventory.append(Pistol(p))
    p.inventory.append(NeoGun(p))
    p.inventory.append(NeoShotgun(p))
    p.activeWeapon = p.inventory[0]

packet = {"command":"STARTCONFIRMATION"}
s.send((json.dumps(packet) + "#").encode())
while running == True:
    print(player.mapX, player.mapY)
    SCREEN.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
        if event.type == pygame.MOUSEBUTTONUP:
            if not pygame.mouse.get_pressed()[0] and event.button == 1 and not player.talking and not player.dead and not player.paused:
                player.fire()

    for bullet in bullets:
        data = bullet.update(enemyList, world.obstacleList)
        if data:
            player.tell_server("hit", data)
    explosions.update()
    player.move(world.obstacleList)
    player.camera.worldAdjust(SCREEN, world, characters, enemyList, npcList)
    player.camera.reAdjust()
    player.camera.bulletAdjust(bullets, explosions)
    player.camera.obstacleAdjust(world.obstacleList)
    player.checkRevive(characters)
    player.checkPause()
    player.hud.animate()
    for p in characters:
        if p == player:
            player.activeWeapon.calcGunAngle()
        else:
            p.activeWeapon.calcGunAngle(True)

    for enemy in enemyList:
        # If enough time has passed
        if pygame.time.get_ticks() - enemy.startTime >= 200 and enemy.startTime:
            enemy.attack()

    world.draw(SCREEN)
    explosions.draw(SCREEN)
    npcList.draw(SCREEN)
    characters.draw(SCREEN)
    world.obstacleList.draw(SCREEN)
    bullets.draw(SCREEN)
    enemyList.draw(SCREEN)
    for p in characters:
        p.activeWeapon.draw(SCREEN)
    player.hud.draw(SCREEN)
    clock.tick(60)
    pygame.display.update()