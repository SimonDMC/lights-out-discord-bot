import math
import random
import discord
import re
from game import Game

REACTIONS = ['⬆️', '➡️', '⬇️', '⬅️', '✅']
games = []

with open("token.txt", "r") as f:
    TOKEN = f.read()

client = discord.Client()


@client.event
async def on_ready():
    print("online")


def switch_sign_at_index(game, i):
    if game.board[int(i)] == "X":
        game.board[int(i)] = "O"
    else:
        game.board[int(i)] = "X"


def is_win(game):
    for i in range(game.boardSize ** 2):
        if game.board[i] != "O":
            return False
    return True


def init_board(board_size):
    board_constructor = []
    for i in range(board_size ** 2):
        board_constructor.append("O")
    for i in range(board_size ** 2):
        to_switch = get_list_to_switch(board_size, random.randrange(0, board_size ** 2))
        for s in range(len(to_switch)):
            if board_constructor[to_switch[s]] == "X":
                board_constructor[to_switch[s]] = "O"
            else:
                board_constructor[to_switch[s]] = "X"
    return board_constructor


def get_board(game):
    to_print = ""
    for i in range(game.boardSize):
        for j in range(game.boardSize):
            index = i * game.boardSize + j  # index of current sign
            current_sign = game.board[index]
            if index == game.selectedSlot:
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
    to_print += "Moves: " + str(game.moves) + "      Flips: " + str(game.flips)
    return to_print


def is_valid_switchable(board_size, i, direction):
    if i < 0:
        return False
    if i >= board_size ** 2:
        return False
    if direction == "r" and i % board_size == 0:
        return False
    if direction == "l" and (i - board_size + 1) % board_size == 0:
        return False
    return True


def get_list_to_switch(board_size, i):
    switch_list = [i]
    if is_valid_switchable(board_size, i - board_size, ""):
        switch_list.append(i - board_size)
    if is_valid_switchable(board_size, i + board_size, ""):
        switch_list.append(i + board_size)
    if is_valid_switchable(board_size, i - 1, "l"):
        switch_list.append(i - 1)
    if is_valid_switchable(board_size, i + 1, "r"):
        switch_list.append(i + 1)
    return switch_list


async def game_loop(game, emoji):
    embed = discord.Embed(title=f"Lights Out! - {game.player.name}", description=get_board(game), color=0x20B702)
    # if the game just started, send message with board and react,
    # otherwise edit and remove user reaction
    if game.msg == 0:
        game.msg = await game.channel.send(embed=embed)
        for reaction in REACTIONS:
            await game.msg.add_reaction(reaction)
    else:
        await game.msg.edit(embed=embed)
        await game.msg.remove_reaction(emoji, game.player)
    if is_win(game):
        await game.msg.edit(content=f'{game.player.mention} won in {game.moves} moves!')
        games.remove(game)
        return


@client.event
async def on_reaction_add(reaction, user):
    for game in games:
        if reaction.message != game.msg:
            continue
        if user != game.player:
            return
        game.moves += 1
        local_slot = game.selectedSlot
        emoji = str(reaction.emoji)
        if emoji == '⬆️':
            local_slot -= game.boardSize
            if local_slot < 0:
                local_slot = game.selectedSlot
        elif emoji == '⬅️':
            local_slot -= 1
            if (local_slot - game.boardSize + 1) % game.boardSize == 0:  # past left border
                local_slot = game.selectedSlot
        elif emoji == '⬇️':
            local_slot += game.boardSize
            if local_slot >= game.boardSize ** 2:
                local_slot = game.selectedSlot
        elif emoji == '➡️':
            local_slot += 1
            if local_slot % game.boardSize == 0:  # past right border
                local_slot = game.selectedSlot
        elif emoji == '✅':
            game.flips += 1
            to_switch = get_list_to_switch(game.boardSize, local_slot)
            for s in to_switch:
                switch_sign_at_index(game, s)
        game.selectedSlot = local_slot
        await game_loop(game, emoji)


async def init_game(game, size):
    game.boardSize = size
    game.selectedSlot = math.floor(game.boardSize ** 2 / 2)
    if game.boardSize % 2 == 0:
        game.selectedSlot -= game.boardSize / 2 + 1  # sets the selected slot to the top left of the middle 4
    game.board = init_board(size)
    await game_loop(game, 0)

# game_stage - 0 = not started; 1 = playing (awaiting input)


@client.event
async def on_message(message):
    user = message.author
    user_message = str(message.content)

    if message.author == client.user:
        return

    if message.channel.name == "lights-out" or message.channel.name == "bot-commands":
        if user_message == "s!start":
            game = Game(user, message.channel)
            # register game in list
            games.append(game)
            await init_game(game, 5)
        # regex matching "s!start " + any number
        elif re.search(r"^(?:s!start )\d+$", user_message):
            # gets just the number by splitting at space and taking the second part (s!start/6)
            num = int(user_message.split(" ")[1])
            if num < 3 or num > 15:
                await message.channel.send("Please choose a value between 3 and 15.")
                return
            game = Game(user, message.channel)
            # register game in list
            games.append(game)
            await init_game(game, num)
        elif user_message == "s!end":
            for game in games:
                if game.player == user:
                    embed = discord.Embed(title=f"Lights Out! - {game.player.name} (Terminated)",
                                          description=get_board(game),
                                          color=0x20B702)
                    await game.msg.edit(embed=embed)
                    games.remove(game)
                    return
            # if user doesn't have any active game
            if message.author.guild_permissions.administrator or \
                    message.author.top_role.permissions.administrator:
                await message.channel.send("All current games were terminated by an administrator.")
                for game in games:
                    embed = discord.Embed(title=f"Lights Out! - {game.player.name} (Terminated)",
                                          description=get_board(game),
                                          color=0x20B702)
                    await game.msg.edit(embed=embed)
                    games.remove(game)
                return
            await message.channel.send("You don't have permission to do that.")


client.run(TOKEN)
