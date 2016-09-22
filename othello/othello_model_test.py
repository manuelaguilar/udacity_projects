#!/usr/bin/python
from othello_logic import OthelloLogic

new_game = OthelloLogic(game_mode="SINGLE PLAYER")
print "GAME STARTED!"
print new_game._getScore()
moves = [ (1,'0'),(1,'1,1'), (1,'3,3'), (1,'6,4'), 
        (1,'4,4'), (1,'3,6'), (1, '4,3'), (2,'1,1') ]

for i in moves:
    isvalid, message = new_game._make_move(i[0], i[1])
    print message
    if isvalid:
        print new_game._getScore()
