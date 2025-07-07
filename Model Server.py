import socket, threading, json, time, pygame
from MapGen import MapGenerator, ServerObstacle
from game_classes import nodeSetup, ServerEnemy, TILE_SIZE, MAP_WIDTH, SCREEN_SIZE

HOST = '127.0.0.1'
PORT = 50000
game = False
clock = pygame.time.Clock()

def recv_from_client(conn,client_list):
    while True:
        data = conn.recv(1024)
        if data:
            instructions = data.decode().split("#")
            packet = json.loads(instructions[0])
            for client in client_list:
                if client != conn:
                    client.send((json.dumps(packet)+"#").encode())
                else:
                    if packet["command"] == "MOVE":
                        players[conn]["location"] = [packet["data"]["xPos"], packet["data"]["yPos"]]

def send_to_client(client_list, packet):
    for client in client_list:
        client.send((json.dumps(packet) + "#").encode())

def gameLoop(players, serverEnemies, client_list):
    while game:
        enemyActions = []
        #Determining the action for each enemy
        for enemy in serverEnemies:
            path = enemy.locate(players, serverNodes)
            enemyActions.append(enemy.travel(path))
            if pygame.time.get_ticks() - enemy.startTime >= 200 and enemy.startTime:
                serverEnemies.remove(enemy)

        packet = {"command":"ENEMYACTIONS", "data":[]}
        for action in enemyActions:
            if action != None:
                if action[1] == "ENEMYMOVE":
                    packet["data"].append({"id":action[0],"action":"MOVE", "x":action[2], "y":action[3]})

                elif action[1] == "ENEMYATTACK":
                    packet["data"].append({"id":action[0], "action": "ATTACK"})

                elif action[1] == "ENEMYDIE":
                    packet["data"].append({"id":action[0], "action": "DIE"})
        send_to_client(client_list, packet)

        clock.tick(60)

#Player and connections
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind( (HOST,PORT) )
client_list = []
players = {}
player_positions = [(1000,1000),(1000,1000)]

#Map
textMap = [['DWater', 'Plains', 'Plains', 'Plains', 'Water', 'DWater', 'Plains', 'Plains', 'Forest', 'Forest', 'Forest', 'Plains', 'Forest', 'Forest', 'Plains', 'Forest', 'Forest', 'Plains', 'Forest', 'Mountain'], ['Forest', 'Water', 'Forest', 'Plains', 'Plains', 'Plains', 'Water', 'Water', 'Water', 'Forest', 'Water', 'Plains', 'Plains', 'Forest', 'Plains', 'Forest', 'Plains', 'Plains', 'Forest', 'Forest'], ['Forest', 'Plains', 'Forest', 'Water', 'Plains', 'Forest', 'Plains', 'Forest', 'Forest', 'Plains', 'Plains', 'Mountain', 'Plains', 'Plains', 'Plains', 'Forest', 'Plains', 'Forest', 'Plains', 'Forest'], ['Forest', 'Plains', 'Water', 'Forest', 'Plains', 'Plains', 'Plains', 'Forest', 'Forest', 'Forest', 'Forest', 'Plains', 'Plains', 'Plains', 'Plains', 'Forest', 'Forest', 'Plains', 'Forest', 'Mountain'], ['Forest', 'Plains', 'Plains', 'Plains', 'Forest', 'Forest', 'Forest', 'Plains', 'Forest', 'Mountain', 'Plains', 'Plains', 'Plains', 'Plains', 'Water', 'Plains', 'Forest', 'HMountain', 'Plains', 'Forest'], ['Forest', 'Plains', 'Forest', 'Forest', 'Water', 'Forest', 'Plains', 'Plains', 'Plains', 'Plains', 'Plains', 'Plains', 'Plains', 'Water', 'Forest', 'Forest', 'HMountain', 'Forest', 'Mountain', 'HMountain'], ['Forest', 'Mountain', 'Forest', 'Plains', 'Plains', 'Plains', 'Forest', 'Mountain', 'Water', 'Plains', 'Forest', 'Forest', 'Plains', 'Mountain', 'Forest', 'Forest', 'Forest', 'Mountain', 'Forest', 'Forest'], ['Plains', 'Plains', 'Water', 'Forest', 'Mountain', 'Plains', 'Plains', 'Plains', 'Water', 'Forest', 'DWater', 'Forest', 'DWater', 'Mountain', 'Plains', 'Mountain', 'Mountain', 'Forest', 'Forest', 'Forest'], ['Mountain', 'Forest', 'Forest', 'Plains', 'Plains', 'Plains', 'Forest', 'Mountain', 'Forest', 'Water', 'Water', 'Mountain', 'Mountain', 'Forest', 'HMountain', 'Mountain', 'Mountain', 'Plains', 'Plains', 'Forest'], ['Water', 'Forest', 'Forest', 'Plains', 'Plains', 'Forest', 'Mountain', 'Water', 'Plains', 'DWater', 'DWater', 'Mountain', 'Water', 'Mountain', 'Forest', 'Forest', 'Forest', 'Plains', 'Forest', 'Mountain'], ['Plains', 'Plains', 'Plains', 'Plains', 'Plains', 'Plains', 'Forest', 'Water', 'Mountain', 'HMountain', 'HMountain', 'Mountain', 'Water', 'Forest', 'Plains', 'Plains', 'Forest', 'Mountain', 'Forest', 'Forest'], ['Forest', 'Forest', 'Mountain', 'Forest', 'Plains', 'Water', 'Forest', 'Water', 'Mountain', 'Forest', 'Water', 'DWater', 'Water', 'Mountain', 'HMountain', 'HMountain', 'Mountain', 'Mountain', 'Mountain', 'Forest'], ['Plains', 'Plains', 'Plains', 'Water', 'Forest', 'Forest', 'Forest', 'Forest', 'HMountain', 'HMountain', 'Mountain', 'Mountain', 'Water', 'Forest', 'Mountain', 'Plains', 'Mountain', 'Mountain', 'Mountain', 'Mountain'], ['Plains', 'Plains', 'Plains', 'Forest', 'Plains', 'Plains', 'Water', 'Plains', 'Forest', 'Mountain', 'DWater', 'DWater', 'HMountain', 'Mountain', 'Forest', 'Forest', 'Forest', 'Forest', 'Plains', 'Plains'], ['Plains', 'Plains', 'Plains', 'Water', 'Plains', 'Plains', 'Mountain', 'Forest', 'Plains', 'Plains', 'Water', 'Forest', 'Mountain', 'Mountain', 'DWater', 'Plains', 'Forest', 'Forest', 'Forest', 'Forest'], ['Plains', 'Forest', 'Forest', 'Plains', 'Plains', 'Plains', 'Forest', 'Forest', 'Water', 'Mountain', 'Plains', 'Forest', 'Plains', 'Mountain', 'Plains', 'Plains', 'Mountain', 'Forest', 'Forest', 'Plains'], ['Forest', 'Forest', 'Plains', 'Forest', 'Plains', 'Forest', 'Forest', 'Forest', 'Forest', 'Forest', 'Plains', 'Mountain', 'Plains', 'Plains', 'Forest', 'Forest', 'Forest', 'Plains', 'Forest', 'Plains'], ['Plains', 'Mountain', 'Forest', 'Plains', 'Plains', 'Plains', 'Mountain', 'Plains', 'Mountain', 'Forest', 'Forest', 'Forest', 'Mountain', 'Forest', 'Plains', 'Water', 'Forest', 'Mountain', 'Forest', 'Plains'], ['Plains', 'Plains', 'Plains', 'Forest', 'Mountain', 'Mountain', 'Forest', 'Forest', 'Forest', 'Forest', 'Forest', 'Plains', 'Plains', 'Forest', 'Forest', 'Water', 'Plains', 'Plains', 'Forest', 'Plains'], ['Plains', 'Forest', 'Forest', 'Forest', 'Forest', 'Plains', 'Plains', 'Forest', 'Plains', 'Plains', 'Forest', 'Forest', 'Mountain', 'Forest', 'Plains', 'Forest', 'Plains', 'Water', 'Forest', 'Mountain']]
mapGen = MapGenerator(textMap)
#textMap = mapGen.generate()
obstacles = mapGen.obstacleGen()
serverObstacles = []
for obstacle in obstacles:
    serverObstacles.append(ServerObstacle(*obstacle))
serverNodes = [[False for count in range(MAP_WIDTH*(SCREEN_SIZE[1]//TILE_SIZE))] for i in range(MAP_WIDTH*(SCREEN_SIZE[0]//TILE_SIZE))]
#this * unpacks the elements
nodes = nodeSetup(serverObstacles, serverNodes)

#Enemies
#Server enemies is a list of the actual objects whereas enemies just contains the data required to send to clients
serverEnemies = []
enemies = []
serverEnemies.append(ServerEnemy(3000, 3000))
serverEnemies.append(ServerEnemy(3000, 4000))
for enemy in serverEnemies:
    enemies.append([enemy.mapX, enemy.mapY, enemy.id])




print("Server is listening on port",PORT)
s.listen(1)
while True:
    conn, addr = s.accept()
    client_list.append(conn)
    print("New Connection from ",addr)
    threading.Thread(target=recv_from_client, args=(conn,client_list)).start()
    if len(client_list) % 2 == 1:
        player_pos = player_positions[0]
        player2_pos = player_positions[1]
        players[conn] = {"location":player_positions[0]}

    else:
        player_pos = player_positions[1]
        player2_pos = player_positions[0]
        players[conn] = {"identity": conn, "location": player_positions[1]}

    message = {"command":"SETUP", "data":{"PlayerX":player_pos[0], "PlayerY":player_pos[1], "EnemyX":player2_pos[0], "EnemyY":player2_pos[1]}}
    conn.send((json.dumps(message)+"#").encode())
    time.sleep(1)
    message = {"command":"OBSTACLES", "data":obstacles}
    conn.send((json.dumps(message)+"#").encode())
    time.sleep(1)
    message = {"command":"ENEMIES", "data":enemies}
    conn.send((json.dumps(message)+"#").encode())
    time.sleep(1)


    # for count in range(len(textMap)):
    # 	if count == len(textMap)-1:
    # 		message = {"command":"MAP", "data":{"Count":"FINAL", "List":textMap[count]}}
    # 	else:
    # 		message = {"command": "MAP", "data": {"Count": count, "List": textMap[count]}}
    # 	conn.send(json.dumps(message).encode())
    # 	time.sleep(1)
    if len(client_list) == 2:
        game = True
        threading.Thread(target=gameLoop, args=(players, serverEnemies, client_list)).start()
        message = {"command": "START"}

        for c in client_list:
            c.send(json.dumps(message).encode())