import math
import random
import discord

TOKEN = "insert token here"

client = discord.Client()


@client.event
async def on_ready():
    print("online")


def switch_sign_at_index(i):
    if board[i] == "X":
        board[i] = "O"
    else:
        board[i] = "X"


def is_win():
    for i in range(boardSize ** 2):
        if board[i] != "O":
            return False
    return True


def init_board():
    board_constructor = []
    for i in range(boardSize ** 2):
        board_constructor.append("O")
    for i in range(boardSize ** 2):
        to_switch = get_list_to_switch(random.randrange(0, boardSize ** 2))
        for s in range(len(to_switch)):
            if board_constructor[to_switch[s]] == "X":
                board_constructor[to_switch[s]] = "O"
            else:
                board_constructor[to_switch[s]] = "X"
    return board_constructor


def get_board():
    to_print = ""
    for i in range(boardSize):
        for j in range(boardSize):
            index = i * boardSize + j  # index of current sign
            current_sign = board[index]
            if index == selectedSlot:
                if current_sign == "X":
                    to_print += "🔵"
                else:
                    to_print += "⚪"
            else:
                if current_sign == "X":
                    to_print += "🟦"
                else:
                    to_print += "⬜"
        to_print += "\n"  # next line, current line iteration ended
    to_print += "Moves: " + str(moves) + "      Flips: " + str(flips)
    return to_print


def is_valid_switchable(i, direction):
    if i < 0:
        return False
    if i >= boardSize ** 2:
        return False
    if direction == "r" and i % boardSize == 0:
        return False
    if direction == "l" and (i - boardSize + 1) % boardSize == 0:
        return False
    return True


def get_list_to_switch(i):
    switch_list = [i]
    if is_valid_switchable(i - boardSize, ""):
        switch_list.append(i - boardSize)
    if is_valid_switchable(i + boardSize, ""):
        switch_list.append(i + boardSize)
    if is_valid_switchable(i - 1, "l"):
        switch_list.append(i - 1)
    if is_valid_switchable(i + 1, "r"):
        switch_list.append(i + 1)
    return switch_list


async def game_loop():
    global game_msg
    embed = discord.Embed(title="Lights Out!", description=get_board(), color=0x20B702)
    game_msg = await channel.send(embed=embed)
    if is_win():
        await channel.send("GG!")
        global game_stage
        game_stage = 0
        return
    await game_msg.add_reaction('⬆️')
    await game_msg.add_reaction('➡️')
    await game_msg.add_reaction('⬇️')
    await game_msg.add_reaction('⬅️')
    await game_msg.add_reaction('✅')


@client.event
async def on_reaction_add(reaction, user):
    if reaction.message == game_msg:
        if str(user) != player:
            return
        global selectedSlot, moves, flips
        moves += 1
        local_slot = selectedSlot
        emoji = str(reaction.emoji)
        if emoji == '⬆️':
            local_slot -= boardSize
            if local_slot < 0:
                local_slot = selectedSlot
        elif emoji == '⬅️':
            local_slot -= 1
            if (local_slot - boardSize + 1) % boardSize == 0:  # past left border
                local_slot = selectedSlot
        elif emoji == '⬇️':
            local_slot += boardSize
            if local_slot >= boardSize ** 2:
                local_slot = selectedSlot
        elif emoji == '➡️':
            local_slot += 1
            if local_slot % boardSize == 0:  # past right border
                local_slot = selectedSlot
        elif emoji == '✅':
            flips += 1
            to_switch = get_list_to_switch(local_slot)
            for s in range(len(to_switch)):
                switch_sign_at_index(to_switch[s])
        selectedSlot = local_slot
        await game_loop()


async def init_game():
    global boardSize, selectedSlot, board, moves, flips
    boardSize = 5
    selectedSlot = math.floor(boardSize ** 2 / 2)
    if boardSize % 2 == 0:
        selectedSlot -= boardSize / 2 + 1  # sets the selected slot to the top right of the middle 4
    board = init_board()
    moves, flips = 0, 0
    await game_loop()


boardSize, selectedSlot, moves, board, flips, player, game_stage, channel, game_msg = [0 for _ in range(9)]


# game_stage - 0 = not started; 1 = playing (awaiting input)


@client.event
async def on_message(message):
    user = str(message.author)
    user_message = str(message.content)

    if message.author == client.user:
        return

    if message.channel.name == "lights-out":
        global game_stage
        if user_message == 's!start_local_game' and game_stage == 0:
            global player, channel
            player = user
            channel = message.channel
            game_stage = 1
            await init_game()


client.run(TOKEN)
