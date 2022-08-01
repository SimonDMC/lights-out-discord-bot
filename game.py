class Game:
    def __init__(self, player, channel):
        self.player = player
        self.channel = channel
        self.boardSize = 0
        self.selectedSlot = 0
        self.board = []
        self.moves = 0
        self.flips = 0
        self.msg = 0
