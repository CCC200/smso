from threading import Thread, active_count
import socket
import pickle
from time import sleep
import os
import sys

serverVersion = '1.0'
playerSlots = [False, False, False, False]
playerSlotsPrint = ["", "", "", ""] # this will have usernames in their correlating slots
portSlots = [False, False, False, False]
port = 8234 # set this to the lowest port you're hosting on. setting it to 8234 means you're hosting on 8234, 8235, 8236, and 8237


level = [0, 0, False]  # [0] = world id, [1] = level id, [2] = if the level will change(false = no change)
gamemode = 0    # 0 = no gamemode, 1 = tag, will add more
tagIt = []
startTag = False
stopFlagSync = False
kickPlayer = 0
tagPlayerTotal = -1
resetTimer = False

def cmdInput():
    global stopFlagSync
    global kickPlayer
    global playerSlots
    global playerSlotsPrint
    global world
    global level
    global gamemode
    global tagIt
    global startTag
    global tagPlayerTotal
    global resetTimer

    levelNames = ["airport", "dolpic", "bianco", "ricco", "gelato", "pinna_beach", "sirena", "hotel", "pianta", "noki", "pinna", "casino"]
    levelNames2 = ["airstrip", "delfino", "bianco_hills", "ricco_harbor", "gelato_beach", "pinna_beach", "sirena_beach", "hotel_delfino", "pianta_village", "noki_bay", "pinna_park", "casino"]
    formal_levelNames = ["Airstrip", "Delfino Plaza", "Bianco Hills", "Ricco Harbor", "Gelato Beach", "Pinna Beach", "Sirena Beach", "Hotel Delfino", "Pianta Village", "Noki Bay", "Pinna Park", "Casino Delfino"]
    levelIDs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14]

    while True:
        #level[1] = ""   # this is done for console feedback reasons
        inputStr = ""
        inputStr = input().lower()
        inputStrArray = inputStr.split()
        try:
            if inputStr == "clear":
                if os.name in ('nt', 'dos'):    # checks the os(if windows, else linux(and maybe mac too? idk what command clears console on mac lol))
                    os.system("cls")
                    print(f"-> CLEARING\n   SMSO Server Version {serverVersion}")
                else:
                    os.system("clear")
                    print(f"-> CLEARING\n   SMSO Server Version {serverVersion}")

            elif inputStr == "stop" or inputStr == "close" or inputStr == "end" or inputStr == "exit":
                print("-> bruh just click x ^_^")

            elif inputStr == "flags on":
                stopFlagSync = False
                print("-> Flags ARE syncing!")
            elif inputStr == "flags off":
                stopFlagSync = True
                print("-> Flags are NOT syncing!")

            elif inputStrArray[0] == "level":
                for i in range(len(levelNames)):
                    if inputStrArray[1] == levelNames[i] or inputStrArray[1] == levelNames2[i]:
                        level[0] = levelIDs[i]
                        try:
                            level[1] = int(inputStrArray[2])
                            try:
                                level[2] = inputStrArray[3]
                            except:
                                level[2] = True
                                #print("here!")
                            print(f"-> Now loading {formal_levelNames[i]}, Episode {level[1] + 1}!")
                            break
                        except:
                            print(f'-> "{level[1]}" is not a number! Please enter a numerical value!')
                            break
                        print("-> Please enter a valid level!")

            elif inputStrArray[0] == "kick":
                if inputStrArray[1] == playerSlotsPrint[0].lower() or inputStrArray[1] == "1" and playerSlots[0] == True:
                    print(f"-> Kicking {playerSlotsPrint[0]}! This will take a few seconds!")
                    kickPlayer = 1
                elif inputStrArray[1] == playerSlotsPrint[1].lower() or inputStrArray[1] == "2" and playerSlots[1] == True:
                    print(f"-> Kicking {playerSlotsPrint[1]}! This will take a few seconds!")
                    kickPlayer = 2
                elif inputStrArray[1] == playerSlotsPrint[2].lower() or inputStrArray[1] == "3" and playerSlots[2] == True:
                    print(f"-> Kicking {playerSlotsPrint[2]}! This will take a few seconds!")
                    kickPlayer = 3
                elif inputStrArray[1] == playerSlotsPrint[3].lower() or inputStrArray[1] == "4" and playerSlots[3] == True:
                    print(f"-> Kicking {playerSlotsPrint[3]}! This will take a few seconds!")
                    kickPlayer = 4
                elif inputStrArray[1] != "1" and inputStrArray[1] != "2" and inputStrArray[1] != "3" and inputStrArray[1] != "4":
                    print(f'-> "{inputStrArray[1]}" is not a recognized username! \n-> Type "slots" to see all connected users!') 
                else:
                    print(f'-> There is not a player in slot {inputStrArray[1]}! \n-> Type "slots" to see all connected users!')

            elif inputStr == "kickall":
                print("-> Kicking all players! This will take a few seconds!")
                kickPlayer = 5

            elif inputStr == "players" or inputStr == "slots":
                print(f"-> Player Slots: {playerSlotsPrint}")

            elif inputStr == "about":
                print("-> Our official Discord server: https://discord.gg/aYHKKDhtuv")

            else:
                print(f'-> "{inputStr}" is not a recognized command!')
        except:
            print("Please actually type something :)")

# Debug functions
isdebug = True # control var

def isDebugOn():
    global isdebug
    if isdebug:
        return True
    return False

def print_debug(s):
    if isDebugOn:
        print(f"{s}")

# Global Flag functions
server_flags = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def storage_write(flags):
    try:
        io_file = open("storage.sav", "w")
        for i in range(len(flags)):
            io_file.write(f"{flags[i]},")
        io_file.close()
    except Exception as e:
        print(f"ERROR: Failed to write to persistent storage!\n{e}")

def storage_init() -> bool:
    global server_flags
    if os.path.exists("storage.sav"):
        try:
            io_file = open("storage.sav")
            io_data = io_file.read().split(",")
            io_file.close()
            for i in range(len(io_data) - 1):
                server_flags[i] = int(io_data[i])
            return True
        except Exception as e:
            print(f"ERROR: Failed to read persistent storage!\n{e}")
    else:
        storage_write(server_flags)
    return False

server_data = [0,0,0,0,[0,0,"",False,False],server_flags]    # index 0-3 = client_data from client(to each specific player). 4 = server data sent to players[0 = level, 1 = gamemode, 2 = who's "it"] 5 = server flag storage

def global_flag_update(client_flags) -> bool:
    global server_flags
    do_update = False
    if client_flags != 0:
        # compare to server & update
        for i in range(0, 73, 8):
            if client_flags[int(i/8)] > server_flags[int(i/8)]:
                print_debug(f"Raising flag {int(i/8)} from {server_flags[int(i/8)]} to {client_flags[int(i/8)]}")
                server_flags[int(i/8)] = client_flags[int(i/8)]
                do_update = True
        for i in range(9, 16):
            if client_flags[i] > server_flags[i]:
                print_debug(f"Raising flag {i} from {server_flags[i]} to {client_flags[i]}")
                server_flags[i] = client_flags[i]
                do_update = True
    if do_update:
        storage_write(server_flags)
    return do_update
#

def client_thread(portOffset):
    global playerSlotsPrint
    global playerSlots
    global kickPlayer
    global portSlots
    global gamemode
    global tagIt
    global startTag
    global tagPlayerTotal
    global resetTimer
    global server_flags
    printConnection = True


    # Create a new socket and connect it to the peer.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((socket.gethostbyname(socket.gethostname()), (port + portOffset)))
    #print(socket.gethostbyname(socket.gethostname()), (8234 + portOffset))    

    portSlots[portOffset] = True

    message, addr = sock.recvfrom(1024)

    sock.connect(addr)

    slotNum = playerSlots.index(False)
    playerSlots[slotNum] = True 

    sock.sendto(pickle.dumps("data received"), addr)

    while True:
        sock.settimeout(3)
        try:
            data = sock.recv(1024)
        except:
            try:
                print(f"[INFO] {server_data[slotNum][3][0]} disconnected!")
            except:
                pass
            playerSlots[slotNum] = False
            playerSlotsPrint[slotNum] = ""
            print(f"       Player Slots: {playerSlotsPrint}") 
            sock.settimeout(None)
            portSlots[portOffset] = False
            server_data[slotNum] = 0
            break
        sock.settimeout(None)

        client_data = pickle.loads(data)

        if printConnection == True:
            printConnection = False
            print(f"[INFO] {client_data[3][0]} connected to port {8234 + portOffset}")
            playerSlotsPrint[slotNum] = client_data[3][0]
            print(f"       Player Slots: {playerSlotsPrint}")

        if client_data[3][1] == True and gamemode == 1:
            try:
                tagIt.index(client_data[3][0])
            except:
                if (len(tagIt) + 1) == tagPlayerTotal:
                    startTag = False
                    tagPlayerTotal = -1
                    tagIt.clear()
                    print(f'-> Everyone has been found for this round! Type "tag add" to set the next tagger!')
                else:
                    tagIt.append(client_data[3][0])

        if stopFlagSync == True: # stops flag data from syncing if it's been disabled
            server_data[5] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif global_flag_update(client_data[2]): #prepare global flag sync
            server_data[5] = server_flags
            print_debug(f"New server data: {server_data[5]}")

        if level[2] == True:    # checks to see if the server is trying to change everyones level
            server_data[4][0] = level
        if level[2] == client_data[3][0]:   # same as above except only changes level for a specific player
            server_data[4][0] = level
            print("here!")

        server_data[4][1] = gamemode
        if gamemode == 1:
            server_data[4][2] = tagIt
        server_data[4][3] = startTag
        server_data[4][4] = resetTimer

        server_data[slotNum] = client_data

        if slotNum == 0:
            indices_to_access_1 = [1, 2, 3, 4, 5]
            accessed_mapping = map(server_data.__getitem__, indices_to_access_1)
            reply = list(accessed_mapping)
        elif slotNum == 1:
            indices_to_access_2 = [0, 2, 3, 4, 5]
            accessed_mapping_2 = map(server_data.__getitem__, indices_to_access_2)
            reply = list(accessed_mapping_2)
        elif slotNum == 2:
            indices_to_access_3 = [0, 1, 3, 4, 5]
            accessed_mapping_3 = map(server_data.__getitem__, indices_to_access_3)
            reply = list(accessed_mapping_3)
        elif slotNum == 3:
            indices_to_access_4 = [0, 1, 2, 4, 5]
            accessed_mapping_4 = map(server_data.__getitem__, indices_to_access_4)
            reply = list(accessed_mapping_4)

        #print(f'Raw Data {sys.getsizeof(reply)}')
        #print(f'Pickled Data {sys.getsizeof(pickle.dumps(reply))}')
        bytenum = sock.sendto(pickle.dumps(reply), addr)

        if kickPlayer == (slotNum + 1):
            kickPlayer = 0
            playerSlots[slotNum] = False
            playerSlotsPrint[slotNum] = ""
            portSlots[portOffset] = False
            server_data[slotNum] = 0
            sleep(3)        # kicks players by timing them out
            print(f"--> {client_data[3][0]} kicked successfully!")
            break
        if kickPlayer == 5:            
            playerSlots[slotNum] = False
            playerSlotsPrint[slotNum] = ""
            portSlots[portOffset] = False
            server_data[slotNum] = 0
            sleep(3)        # kicks players by timing them out
            print(f"--> {client_data[3][0]} kicked successfully!")
            kickPlayer = 0
            break

print(f"[STARTING] Running Server Version {serverVersion}")

for i in range(4):
    th = Thread(target=client_thread, args=(i,))
    th.start()
    #print(active_count() - 1)  #prints the amound of receiveThreads

cmdThread = Thread(target = cmdInput)
cmdThread.start()

print(f"[INFO] Server listening on {socket.gethostbyname(socket.gethostname())}") 

if storage_init(): # load global flags from storage
    print("[INFO] Progress flags loaded from persistent storage!")
    print_debug(server_flags)

while True:
    sleep(2.5)
    level[2] = False
    resetTimer = False
    if active_count() != 6:         # active_count() is the amount of threads running
        th = Thread(target=client_thread, args=(portSlots.index(False),))
        th.start()
