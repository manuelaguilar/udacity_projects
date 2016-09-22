from pprint import pprint

class OthelloLogic:


    def __init__(self, game_mode="SINGLE PLAYER"):
        self.game_mode = game_mode
        #board
        self.B = [[0]*8 for i in range(8)] 
        #init positions
        # 1: player 1 piece
        # 2: player 2 piece
        self.B[3][3] = self.B[4][4] = 1
        self.B[3][4] = self.B[4][3] = 2
    
        #current turn (1: user 1, 2:user 2 or CPU)
        self.CP = 1 
        #check move
        self.C = [0] * 8

        #posible displacements
        # -1 : left or upwards
        # 1 : right or down
        self.D = [ [ -1,-1 ],
                [ 0,-1 ],
                [ 1,-1 ],
                [ -1,0 ],
                [ 1,0 ],
                [ -1,1 ],
                [ 0,1 ],
                [ 1,1 ] ]
        # To keep track of CPU moves
        self.X = [0] * 60 
        self.Y = [0] * 60
        self.N = [0] * 60
        
        # initial score (2 pieces, each)
        #self.CS=0
        #self.PS=0
    
    def _make_move(self, CP, move):
        print 'Requesting move for player {0} with coords {1}'.format(CP, move)
    
        # this is just to follow the classic implementation in BASIC
        # '0' is another way for a user input to cancel the game
        # for now I will just ignore it because I'd have to 
        # rewrite the cancel_game endpoint
        if move == "0":
            return (False, "Not implemented")
        opponent = 1 if self.CP == 2 else 2 
        # this will yield the move to the next player
        if move == "9":
            self.CP = opponent 
            return (True, "Player passes. It's player {0}'s turn".format(opponent))
        # check gaming mode
        if self.game_mode == "SINGLE PLAYER" and CP == 2:
            return (False, "This is a single player game! You could "
                    "cancel it and create a two player game. =)")
        coord = dict(zip(['row', 'col'], map(int,move.split(","))))
        print coord
        row = coord.get('row')
        col = coord.get('col')

        if (row < 1 or row > 8) or (col < 1 or col > 8):
            return (False, 'Invalid coordinates')
        # check if board cell is taken
        if self.B[row-1][col-1] is not 0:
            return (False, "Cell is already occupied")
        NF = 0
        for f in range(0,8):
            CF = 0
            if row+self.D[f][0] == 9 or row+self.D[f][0] == 0:
                self.C[f] = 0
                if CF == 1:
                    self.C[f] = f
                    continue
            if col+self.D[f][1]==9 or col+self.D[f][1] == 0:
                self.C[f] = 0
                if CF == 1:
                    self.C[f] = f
                    continue
            if self.B[(row-1)+self.D[f][0]][col-1 +\
                    self.D[f][1]] == opponent:
                CF = 1
                NF = 1
                self.C[f] = 0
                if CF == 1:
                    self.C[f] = f
        if NF is not 1:
            return (False, "Your piece has to be next to an opponent's")
        RF = 0
        print "debug C", self.C
        #scan for possible line colonization
        for q in range(0,8):
            if self.C[q] == 0:
                #line is broken
                continue
            XP = row
            YP = col
            while True:
                XP = XP + self.D[q][0]
                YP = YP + self.D[q][1]
                if ( XP == 0 or XP == 9 ) or ( YP == 0 or YP == 9 ):
                    self.C[q]=0
                    break
                if self.B[XP-1][YP-1] == self.CP:
                    RF = 1
                    break
                #if B[XP-1][YP-1] == opponent
                if self.B[XP-1][YP-1] == 0:
                    self.C[q]=0
                    break
        if RF == 0:
            return (False, "Your move doesn't close an opponent's line")
        #updates board with new move
        for q in range(0,8):
            if self.C[q] == 0:
                continue
            XP = row-1 + self.D[q][0]
            YP = col-1 + self.D[q][1]
            while self.B[XP][YP] is not self.CP:
                self.B[XP][YP]=self.CP
                XP = XP + self.D[q][0]
                YP = YP + self.D[q][1]
        self.B[row-1][col-1] = self.CP
        self.CP=opponent
        return (True, "Move is completed, player's {0} turn!".format(self.CP))
    
    def _getScore(self):
        #local counters
        CS = 0
        PS = 0
        """ Scan the board and compute points """
        for r in self.B:
            for c in r:
                if c == 1:
                    CS+=1
                if c == 2:
                    PS+=1
        print "Debug board"
        print "Points player 1:", CS
        print "Points player 2:", PS
        pprint(self.B)
        return (CS, PS)
   

