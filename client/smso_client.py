import socket
import pickle
from dolphin import event, memory, gui
from threading import Thread
from time import sleep

connected = 1              # 0 = disconnected, 1 = connecting, 2 = connected
gamemodeOffset = 0x80431140
hasDied = False
setTimer = True
clientVersion = 'c1.0'

# reads options.txt
def readOptions() -> str:
    try:    # i "try-execpt" instead of "with" here bc i only want to create a new txt if it doesn't exist
        optionTxt = open("options.txt")
    except:
        optionTxt = open("options.txt", "w")

    # declares are sets up each var
    read_option_str = ["username", "ip", "port"]
    option_line = "nop"
    split_array = ["nop", "nop"]

    for i in range(0, 3, 1): # the second param = how many lines in options.txt to interpret
        option_line = optionTxt.readline()  # reads each line of options.txt(automatically reads the next line each subsequent time ran)
        split_array = option_line.split()   # splits each line into it's label( put into split_array[0]) and parameter(put into split_array[1])
        read_option_str[i] = split_array[1]    # since only the parameter is needed, split_array[1] is the only thing transfered to read_option_str[i], which is returned later

    optionTxt.close()
    return read_option_str


optionStr = readOptions()   # optionStr[0] = username, [1] = ip, [2] = port
username = optionStr[0] # gets the username for future use
tagAdd = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = (optionStr[1], int(optionStr[2]))

sock.settimeout(1)
for i in range(1, 5, 1):
    try:
        sock.sendto(pickle.dumps("test connection"), addr)
        data, testAddr = sock.recvfrom(1024)
        break
    except:
        addr = (optionStr[1], int(optionStr[2]) + i)
sock.settimeout(3)
            
previous_spam_state = [0,0]

def getClientPosData(gpMarioOriginal, gpApplication, gpMarDirector):
    position_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    position_data[0] = memory.read_f32(gpMarioOriginal + 0x10) # x position
    position_data[1] = memory.read_f32(gpMarioOriginal + 0x14) # y position
    position_data[2] = memory.read_f32(gpMarioOriginal + 0x18) # z position
    position_data[3] = memory.read_u16(gpMarioOriginal + 0x94) # x angle
    position_data[4] = memory.read_u16(gpMarioOriginal + 0x96) # y angle
    position_data[5] = memory.read_u16(gpMarioOriginal + 0x98) # z angle
    position_data[6] = memory.read_u16(gpMarioOriginal + 0x90) # acceleration direction
    position_data[7] = memory.read_u32(gpMarioOriginal + 0x78) # unknown
    position_data[8] = memory.read_f32(gpMarioOriginal + 0xEB8) # unknown
    position_data[9] = memory.read_f32(gpMarioOriginal + 0x8C) # base acceleration

    return position_data


def getClientStateData(gpMarioOriginal, TWaterGunPointer, gpApplication, gpMarDirector, TMarioController, TYoshi, TMarioCap):
    state_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    state_data[0] = memory.read_u8(gpMarDirector + 0x64) # game state 1
    state_data[1] = memory.read_u8(gpApplication + 0xE) # gets current stage 1
    state_data[2] = memory.read_u8(gpApplication + 0xF) # gets current stage 2
    state_data[3] = memory.read_u32(gpMarioOriginal + 0x7C) # current state
    state_data[4] = memory.read_u32(gpMarioOriginal + 0x80) # previous state
    state_data[5] = memory.read_u32(gpMarioOriginal + 0x84) # substate
    state_data[6] = memory.read_u64(TWaterGunPointer + 0x1C80) # gets FLUDD's values
    state_data[7] = memory.read_u32(gpMarioOriginal + 0x118) # mario flags
    state_data[8] = memory.read_f32(gpMarioOriginal + 0xB0) # forward speed
    state_data[9] = memory.read_u16(gpMarioOriginal + 0x96) # mario angles 1
    state_data[10] = memory.read_u16(gpMarioOriginal + 0x120) # mario health
    state_data[11] = memory.read_u32(gpMarioOriginal + 0x74) # inputs
    state_data[12] = memory.read_u32(TMarioController + 0x1C) # gets R button inputs
    state_data[13] = memory.read_u32(gpMarioOriginal + 0x380) # fludd animations
    state_data[14] = memory.read_u16(TWaterGunPointer + 0x37A) # fludd angle
    state_data[15] = memory.read_u8(TYoshi) # yoshi state
    state_data[16] = memory.read_u32(TYoshi + 0xC) # juice level
    state_data[17] = memory.read_u32(TYoshi + 0xB8) # flutter
    state_data[18] = memory.read_u8(TWaterGunPointer + 0x715) # spam spray "state"
    state_data[19] = memory.read_u8(TWaterGunPointer + 0x153D) # spam spray "state" for yoshi
    state_data[20] = memory.read_u32(gpMarioOriginal + 0x384) # grab target
    state_data[21] = memory.read_u8(TMarioCap + 0x5) # sunglasses

    return state_data

def getClientFlagData(TFlagManager):
    flag_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(0, 73, 8):
        flag_data[int(i/8)] = memory.read_u64(TFlagManager + i)
    flag_data[9] = memory.read_u64(TFlagManager + 0x6D)
    flag_data[10] = memory.read_u32(TFlagManager + 0xD0)
    flag_data[11] = memory.read_u32(TFlagManager + 0xD4)
    flag_data[12] = memory.read_u8(TFlagManager + 0x6C)
    flag_data[13] = memory.read_u32(TFlagManager + 0x70)
    flag_data[14] = memory.read_u16(TFlagManager + 0x74)
    flag_data[15] = memory.read_u8(TFlagManager + 0xCD)

    return flag_data

def send(client_data):
    global connected
    if connected == 0:
        raise Exception("connected == False!")
    sock.sendto(pickle.dumps(client_data), addr)


def gamemode(server_data, gpMarioOriginal, gpMarDirector, client_game_state):
    global tagAdd
    global hasDied
    global setTimer
    TMarioCap = memory.read_u32(gpMarioOriginal + 0x3E0)
    TMarioGamepad = memory.read_u32(gpMarioOriginal + 0x4FC)

    if tagAdd == True:
        tagAdd = False

    memory.write_u32(gamemodeOffset, server_data[3][1])     # this writes the gamemode

    if server_data[3][3] == True:
        memory.write_u32(gamemodeOffset - 0x4, 1)
        if setTimer == True:
            memory.write_u32(gamemodeOffset + 0x18, 1)  # startTimer variable in the memory
            setTimer = False
    else:
        memory.write_u32(gamemodeOffset - 0x4, 0)   # tagBool variable in the memory
        memory.write_u32(gamemodeOffset + 0x10, 0)  # isTagger variable in the memory
        hasDied = False
        tagAdd = False
        setTimer = True

    if server_data[3][4] == True:
        memory.write_u32(gamemodeOffset - 0x8, 0)   # clientTagTime variable in the memory

    if memory.read_u32(gamemodeOffset - 0x4) == 1 and memory.read_u8(gpMarDirector + 0x64) == 7:
        hasDied = True

    if memory.read_u32(gamemodeOffset - 0x4) == 1 and hasDied == True:
        try:
            server_data[3][2].index(username)
            hasDied = False
        except:
            tagAdd = True
            hasDied = False

    if client_game_state != 9 and client_game_state != 0:
        try:
            server_data[3][2].index(username)
            memory.write_u32(gamemodeOffset + 0x10, 1)  # isTagger variable in the memory
        except:
            memory.write_u32(gamemodeOffset + 0x10, 0)  # isTagger variable in the memory
             
        try:
            server_data[3][2].index(username)
            shirtFlag = memory.read_u8(gpMarioOriginal + 0x119)
            if (shirtFlag << 3) < 128:
                shirtFlag += 0x10
                memory.write_u8(gpMarioOriginal + 0x119, shirtFlag)
                memory.write_u8(TMarioCap + 0x5, 0x5)
        except:
            shirtFlag = memory.read_u8(gpMarioOriginal + 0x119)
            if (shirtFlag << 3) >= 128:
                shirtFlag -= 0x10
                memory.write_u8(gpMarioOriginal + 0x119, shirtFlag)
                memory.write_u8(TMarioCap + 0x5, 0x1)

# debug functions
isdebug = False # control var
hasupdated = False
debugdata = 0

def isDebugOn() -> bool:
    global isdebug
    if isdebug:
        return True
    return False

# Global Flags
global_flags = 0

def receive():
    # gui.draw_text((11,45), 0xffff0000, "Receiving")
    global connected
    global addr
    global global_flags
    global hasupdated # debug
    global debugdata # debug
    #global username
    while True:
        hasupdated = False
        try:
            data, receiveAddr = sock.recvfrom(2048)
            connected = 2
        except Exception as e:
            connected = 0
            print(f"EXCEPTION -> {e}")
            break
        else:
            server_data = pickle.loads(data)
            for number in range(len(server_data) - 2):
                gpMarioNew = memory.read_u32(0x804303DC + (number * 4))
                gpMarioOriginal = memory.read_u32(0x8040E0E8)
                gpMarDirector = memory.read_u32(0x8040E178)
                client_game_state = memory.read_u8(gpMarDirector + 0x64)
                TPauseMenu2 = memory.read_u32(gpMarDirector + 0xAC)
                if server_data[number] != 0:
                    gpApplication = memory.read_u32(0x803E9700)
                    TWaterGunPointer = memory.read_u32(gpMarioNew + 0x3E4)
                    TNewMarioController = memory.read_u32(gpMarioNew + 0x108)
                    TYoshi = memory.read_u32(gpMarioNew + 0x3F0)
                    TMarioNewCap = memory.read_u32(gpMarioNew + 0x3E0)
                    server_game_state = server_data[number][1][0]
                    client_stage1 = memory.read_u8(gpApplication + 0xE)
                    server_stage1 = server_data[number][1][1]
                    server_stage2 = server_data[number][1][2]
                    if server_data[number][1][1] == 0x1 and server_data[number][1][2] == 0x09 and memory.read_u16(gpApplication + 0xE) != 0x109:  # checks to see if another player is in dolpic 9(flooded plaza)
                        server_data[number][0][1] += 1000  # since dolpic 9 is lower on the y axis than the other plazas, we 1000 back to sync it
                    if memory.read_u16(gpApplication + 0xE) == 0x109 and server_data[number][1][1] == 0x1 and server_data[number][1][2] != 0x09:  # checks to see if the player is in dolpic 9, but not other players
                        server_data[number][0][1] -= 1000  # since dolpic 9 is lower on the y axis than the other plazas, we subtract 1000 back to sync it

                    try:
                        if server_data[3][0][2] == True or server_data[3][0][2] == username.lower():    # this sets everyone's stage
                            memory.write_u8(TPauseMenu2 + 0x109, 9)                                     # tells our custom asm to change stage
                            memory.write_u8(gpApplication + 0x13, server_data[3][0][1])                 # episode id
                            memory.write_u8(gpApplication + 0x12, server_data[3][0][0])                 # world id
                            memory.write_u8(gpMarDirector + 0x64, 5)                                    # game state
                            memory.write_u32(TPauseMenu2 + 0x10, 5)                                     # pause state?
                            memory.write_u8(TPauseMenu2 + 0xE0, 2)                                      # active pause menu element
                            server_data[3][0][2] == False
                    except:
                        pass

                    #username = server_data[3][0]

                    #gamemode(server_data, gpMarioOriginal, gpMarDirector, client_game_state)    # this function deals with all the gamemode stuff | commented out for 120

                    if client_stage1 == server_stage1 and client_game_state != 9 and client_game_state != 0 and server_stage2 != 0xFF and gpMarioNew != gpMarioOriginal and server_game_state != 9 and server_game_state != 0:
                        if memory.read_u8(gpMarioNew + 0x115) == 0x10 and server_game_state != 1:
                            memory.write_u32(gpMarioNew + 0x7C, 0x00001337)
                            break
                        x = float(server_data[number][0][0])
                        y = float(server_data[number][0][1])
                        z = float(server_data[number][0][2])
                        x_ang = server_data[number][0][3]
                        y_ang = server_data[number][0][4]
                        z_ang = server_data[number][0][5]
                        acc = server_data[number][0][6]
                        unk = server_data[number][0][7]
                        unk2 = float(server_data[number][0][8])
                        base_acc = float(server_data[number][0][9])

                        state1 = server_data[number][1][3]
                        state2 = server_data[number][1][4]
                        state3 = server_data[number][1][5]
                        fludd_vals = server_data[number][1][6]
                        mario_flags = server_data[number][1][7]
                        forward_speed = float(server_data[number][1][8])
                        mario_angles_1 = server_data[number][1][9]
                        health = server_data[number][1][10]
                        inputs = server_data[number][1][11]
                        r_button = server_data[number][1][12]
                        # fludd_anim = server_data[number][1][13]
                        fludd_angle = server_data[number][1][14]
                        yoshi_state = server_data[number][1][15]
                        juice_level = server_data[number][1][16]
                        flutter = server_data[number][1][17]

                        spam_spray = server_data[number][1][18]
                        if previous_spam_state[0] == 0 and spam_spray == 2:
                            previous_spam_state[0] = 1
                        else:
                            previous_spam_state[0] = spam_spray

                        yoshi_spam_spray = server_data[number][1][19]
                        if previous_spam_state[1] == 0 and yoshi_spam_spray == 2:
                            previous_spam_state[1] = 1
                        else:
                            previous_spam_state[1] = yoshi_spam_spray

                        grab_target = server_data[number][1][20]
                        sunglasses = server_data[number][1][21]

                        memory.write_f32(gpMarioNew + 0x10, x)
                        memory.write_f32(gpMarioNew + 0x14, y)
                        memory.write_f32(gpMarioNew + 0x18, z)
                        memory.write_u16(gpMarioNew + 0x94, x_ang)
                        memory.write_u16(gpMarioNew + 0x96, y_ang)
                        memory.write_u16(gpMarioNew + 0x98, z_ang)
                        memory.write_u16(gpMarioNew + 0x90, acc)
                        memory.write_u32(gpMarioNew + 0x78, unk)
                        memory.write_f32(gpMarioNew + 0xEB8, unk2)
                        memory.write_f32(gpMarioNew + 0x8C, base_acc)

                        if state1 == 0x10020370:
                            print("YES")
                        if state1 == 0x00001336 or state1 == 0x2FFCFFE8 or state1 == 0x00001302 or state1 == 0x10100341 or state1 == 0x18100340 or state1 == 0x10100343 or state1 == 0x00000350 or state1 == 0x00000351 or state1 == 0x00000352 or state1 == 0x0000035B or state1 == 0x00000353 or state1 == 0x0000035C or state1 == 0x10000357 or state1 == 0x10000556 or state1 == 0x10000554 or state1 == 0x10000358 or state1 == 0x00810446 or state1 == 0x10001308:
                            pass
                        else:
                            memory.write_u32(gpMarioNew + 0x7C, state1)
                            memory.write_u32(gpMarioNew + 0x80, state2)
                            memory.write_u32(gpMarioNew + 0x84, state3)
                        memory.write_u64(TWaterGunPointer + 0x1C80, fludd_vals)
                        if mario_flags != 0x00008100:
                            memory.write_u32(gpMarioNew + 0x118, mario_flags)
                        memory.write_f32(gpMarioNew + 0xB0, forward_speed)
                        memory.write_u16(gpMarioNew + 0x96, mario_angles_1)
                        memory.write_u16(gpMarioNew + 0x120, health)
                        memory.write_u32(gpMarioNew + 0x74, inputs)
                        memory.write_u32(TNewMarioController + 0x1C, r_button)
                        # memory.write_u32(gpMarioNew + 0x380, fludd_anim)
                        memory.write_u16(TWaterGunPointer + 0x37A, fludd_angle)
                        memory.write_u8(TYoshi, yoshi_state)
                        memory.write_u32(TYoshi + 0xC, juice_level)
                        memory.write_u32(TYoshi + 0xB8, flutter)
                        memory.write_u8(TWaterGunPointer + 0x715, previous_spam_state[0])
                        memory.write_u8(TWaterGunPointer + 0x153D, previous_spam_state[1])
                        # memory.write_u32(gpMarioNew + 0x384, grab_target)
                        memory.write_u8(TMarioNewCap + 0x5, sunglasses)
                    else:
                        if gpMarioNew != gpMarioOriginal and client_game_state != 9 and client_game_state != 0:
                            memory.write_u32(gpMarioNew + 0x7C, 0x0000133F)
                else:
                    if gpMarioNew != gpMarioOriginal and client_game_state != 9 and client_game_state != 0:
                        memory.write_u32(gpMarioNew + 0x7C, 0x0000133F)
            # Global Flags
            if global_flags != server_data[4]: #compare global flags for debug
                hasupdated = True
            global_flags = server_data[4]
            debugdata = global_flags
            TFlagManager = memory.read_u32(0x8040E160)
            client_flag_data = getClientFlagData(TFlagManager)
            for i in range(0, 73, 8):
                if global_flags[int(i/8)] > client_flag_data[int(i/8)]:
                    memory.write_u64(TFlagManager + i, global_flags[int(i/8)])
            if global_flags[9] > client_flag_data[9]:
                memory.write_u64(TFlagManager + 0x6D, global_flags[9])
            if global_flags[10] > client_flag_data[10]:
                memory.write_u32(TFlagManager + 0xD0, global_flags[10])
            if global_flags[11] > client_flag_data[11]:
                memory.write_u32(TFlagManager + 0xD4, global_flags[11])
            if global_flags[12] > client_flag_data[12]:
                memory.write_u8(TFlagManager + 0x6C, global_flags[12])
            if global_flags[13] > client_flag_data[13]:
                memory.write_u32(TFlagManager + 0x70, global_flags[13])
            if global_flags[14] > client_flag_data[14]:
                memory.write_u16(TFlagManager + 0x74, global_flags[14])
            if global_flags[15] > client_flag_data[15]:
                memory.write_u8(TFlagManager + 0xCD, global_flags[15])
    sleep(1)    # if the thread is about to break, makes sure connected is set to false(it can stay true w/o this with some unfortunate timing)
    connected = 0
    sleep(1)
    connected = 0

def main(frame):
    global connected
    global hasupdated # debug
    global debugdata # debug

    gui.draw_text((11,29), 0xff3d3d3d, f"Client Version: {clientVersion}")

    gpMarioOriginal = memory.read_u32(0x8040E0E8)
    gpApplication = memory.read_u32(0x803E9700)
    gpMarDirector = memory.read_u32(0x8040E178)
    TWaterGunPointer = memory.read_u32(gpMarioOriginal + 0x3E4)
    TYoshi = memory.read_u32(gpMarioOriginal + 0x3F0)
    TMarioController = memory.read_u32(gpMarioOriginal + 0x108)
    TFlagManager = memory.read_u32(0x8040E160)
    TMarioCap = memory.read_u32(gpMarioOriginal + 0x3E0)

    client_data = [0, 0, 0, [0,0]]      # what gets sent to the server; 0 = position data, 1 = state data, 2 = flag data, 3 = username
    client_data[0] = getClientPosData(gpMarioOriginal, gpApplication, gpMarDirector)
    client_data[1] = getClientStateData(gpMarioOriginal, TWaterGunPointer, gpApplication, gpMarDirector, TMarioController, TYoshi, TMarioCap)
    if frame == 0:  # only send/get flag data once per second bc it doesnt need to immediatly update
        client_data[2] = getClientFlagData(TFlagManager)
    client_data[3][0] = username
    client_data[3][1] = tagAdd

    try:
        send(client_data) # sends client data to send function
    except:
        gui.draw_text((10,5), 0xffff0000, f"Disconnected!") # tells user that they are disconnected
        memory.write_u32(gamemodeOffset + 0xC, 0)   # connected variable in the memory
    else:
        if connected == 2:
            gui.draw_text((10,5), 0xff00ff00, f"Connected!") # tells user that they are connected
            gui.draw_text((10,17), 0xff00ff00, f"Username: {username}") # prints username on screen
            memory.write_u32(gamemodeOffset + 0xC, 1)   # connected variable in the memory
            if isDebugOn():
                gui.draw_text((11,45), 0xffff0000, f"Update: {hasupdated}")
                gui.draw_text((11,60), 0xffff0000, f"{debugdata}")
        elif connected == 1:
            gui.draw_text((10,5), 0xffffff00, f"Connecting...") # tells user that they are connected
        



if __name__ == '__main__':
    receiveThread = Thread(target = receive)
    receiveThread.start()  # starts a thread to always be recieving data

    while True: # put a for loop in here to count frames for sending flag data
        for frame in range(30):
            await event.frameadvance()
            await event.frameadvance()
            main(frame)
