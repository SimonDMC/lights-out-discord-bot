class Game:
    def __init__(self, player):
        self.player = player
        self.boardSize = 0
        self.selectedSlot = 0
        self.board = []
        self.moves = 0
        self.flips = 0
        self.msg = 0
