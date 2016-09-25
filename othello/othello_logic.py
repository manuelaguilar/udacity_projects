from pprint import pprint
DEFAULT_GAME_MODE = "SINGLE_PLAYER"

# OTHELLO C64 - OTELO PARA COMMODORE 64 BASIC
# THIS IMPLEMENTATION WAS PORTED FROM INPUT
# COMMODORE, A SPANISH MAGAZINE FROM THE EARLY
# 1980 YEARS.
# THE USE OF ARRAYS, MATRICES,  AND ABUNDANCE
# OF CONTROL FLOW KEYWORDS LIKE break and
# continue ARE MEANT TO MIMIC THE BEHAVIOR OF
# THIS OLD PROGRAMMING LANGUAGE,
# MAINLY THE USE OF GOTO STATEMENTS.


class OthelloLogic:

    def __init__(self, game_mode=DEFAULT_GAME_MODE):
        self.game_mode = game_mode
        # board
        self.B = [[0]*8 for i in range(8)]
        # init positions
        # 1: player 1 pieces
        # 2: player 2 pieces
        self.B[3][3] = self.B[4][4] = 1
        self.B[3][4] = self.B[4][3] = 2

        # current turn (1: user 1, 2:user 2 or CPU)
        self.CP = 1
        # check move array
        self.C = [0] * 8

        # posible displacement vectors
        # -1 : left or upwards
        # 1 : right or down
        self.D = [[-1, -1],
                  [0, -1],
                  [1, -1],
                  [-1, 0],
                  [1, 0],
                  [-1, 1],
                  [0, 1],
                  [1, 1]]
        # To keep track of CPU moves
        self.X = [0] * 60
        self.Y = [0] * 60
        self.N = [0] * 60

    def _make_move(self, CP, move):

        # this is just to follow the implementation
        # '0' is another way for a user input to cancel the game
        # for now I will just ignore it because I'd have to
        # rewrite the cancel_game endpoint
        if move == "0":
            return (False, "Not implemented")
        opponent = 1 if self.CP == 2 else 2
        if self.CP != CP:
            return (False, "It's player's {0} turn!".format(self.CP))
        # this will yield the move to the next player
        if move == "9":
            self.CP = opponent
            return (True, "Player passes. It's player {0}'s turn".
                    format(opponent))
        # check gaming mode
        print 'Requesting move for player {0} with coords {1}'.format(CP, move)
        if self.game_mode == DEFAULT_GAME_MODE and self.CP == 2:
            return (False, "This is a single player game! You could "
                    "cancel it and create a two player game. =)")
        coord = dict(zip(['row', 'col'], map(int, move.split(","))))
        print coord
        row = coord.get('row')
        col = coord.get('col')

        if (row < 1 or row > 8) or (col < 1 or col > 8):
            return (False, 'Invalid coordinates')
        # check if board cell is taken
        if self.B[row-1][col-1] is not 0:
            return (False, "Cell is already occupied")
        NF = 0
        for f in range(0, 8):
            CF = 0
            if row+self.D[f][0] == 9 or row+self.D[f][0] == 0:
                self.C[f] = 0
                if CF == 1:
                    self.C[f] = f
                continue
            if col+self.D[f][1] == 9 or col+self.D[f][1] == 0:
                self.C[f] = 0
                if CF == 1:
                    self.C[f] = f
                continue
            if self.B[(row-1) +
                      self.D[f][0]][(col-1) +
                                    self.D[f][1]] == opponent:
                print "Found opponent", opponent, f
                CF = 1
                NF = 1
                self.C[f] = 0
                if CF == 1:
                    # mark as checked, valid
                    self.C[f] = 1
        if NF is not 1:
            return (False, "Your piece has to be next to an opponent's")
        RF = 0
        print "debug C", self.C
        # scan for possible line colonization
        for q in range(0, 8):
            # check if direction to follow is marked
            if self.C[q] == 0:
                # line is broken
                continue
            XP = row
            YP = col
            while True:
                XP = XP + self.D[q][0]
                YP = YP + self.D[q][1]
                if (XP == 0 or XP == 9) or (YP == 0 or YP == 9):
                    self.C[q] = 0
                    break
                if self.B[XP-1][YP-1] == self.CP:
                    RF = 1
                    break
                if self.B[XP-1][YP-1] == 0:
                    self.C[q] = 0
                    break
        if RF == 0:
            return (False, "Your move doesn't close an opponent's line")
        # updates board with new move
        for q in range(0, 8):
            # if route is valid, update board
            if self.C[q] == 0:
                continue
            XP = row-1 + self.D[q][0]
            YP = col-1 + self.D[q][1]
            while self.B[XP][YP] is not self.CP:
                self.B[XP][YP] = self.CP
                XP = XP + self.D[q][0]
                YP = YP + self.D[q][1]
        self.B[row-1][col-1] = self.CP
        self.CP = opponent

        return (True, "Move is completed, player's {0} turn!".format(self.CP))

    def _cpu_move(self):
        if self.game_mode == "TWO PLAYER":
            return False, "I'm not supposed to be playing. "
            "You have to be in single"
            " player mode for that. Maybe create a new game?"
        if self.CP is not 2:
            return False, "It's not my turn. I'm going to pass."
        print "CPU is going to move"
        NF = 0
        MX = 0
        # manuel - needed to flag end of f loop from within while block
        EL_1 = False
        # sequential scan for every free cell
        for x in range(0, 8):
            for y in range(0, 8):
                if self.B[x][y] is not 0:
                    continue
                for f in range(0, 8):
                    XP = x
                    YP = y
                    DX = self.D[f][0]
                    DY = self.D[f][1]
                    RF = 0
                    while True:
                        XP = XP+DY
                        YP = YP+DX
                        if (XP+1 == 0 or XP+1 == 9) or\
                           (YP+1 == 0 or YP+1 == 9):
                            break
                        if self.B[XP][YP] == 1:
                            RF = 1
                        else:
                            if self.B[XP][YP] == 2 and RF == 1:
                                self.N[NF] = f
                                self.X[NF] = x
                                self.Y[NF] = y
                                NF = NF+1
                                EL_1 = True
                            break
                    if EL_1:
                        EL_1 = False
                        break

        if NF == 0:
            # yield turn
            self.CP = 1
            return False, "I cannot make a move. Yield to you."
        for f in range(0, NF):
            X = self.X[f]
            Y = self.Y[f]
            DX = self.D[self.N[f]][0]
            DY = self.D[self.N[f]][1]
            CF = 0
            while True:
                X = X+DY
                Y = Y+DX
                if self.B[X][Y] == 1:
                    CF = CF+1
                else:
                    break
            if CF > MX:
                MX = CF
                MF = f
        EL_1 = False
        for f in range(0, 8):
            X = self.X[MF]
            Y = self.Y[MF]
            DX = self.D[f][0]
            DY = self.D[f][1]
            while True:
                X = X+DY
                Y = Y+DX
                if X < 0 or X > 7 or Y < 0 or Y > 7:
                    break
                if self.B[X][Y] == 1:
                    continue
                if self.B[X][Y] == 2:
                    X = self.X[MF]
                    Y = self.Y[MF]
                    # CPU colonizes line
                    while True:
                        self.B[X][Y] = 2
                        X = X+DY
                        Y = Y+DX
                        if self.B[X][Y] == 2:
                            EL_1 = True
                            break
                break
        # return turn to player
        self.CP = 1
        return True, ("My move: {0}, {1}".format(self.X[MF]+1, self.Y[MF]+1))

    def _getScore(self):
        """ Scan the board and compute points """
        # local counters
        CS = 0
        PS = 0
        for r in self.B:
            for c in r:
                if c == 1:
                    CS += 1
                if c == 2:
                    PS += 1
        print "Debug board"
        print "Points player 1:", CS
        print "Points player 2:", PS
        pprint(self.B)
        return (CS, PS)

    def _isBoardFull(self):
        CS, PS = self._getScore()
        return CS+PS == 64
