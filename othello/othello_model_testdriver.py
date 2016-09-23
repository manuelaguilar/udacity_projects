#!/usr/bin/python
from othello_logic import OthelloLogic

new_game = OthelloLogic(game_mode="SINGLE PLAYER")
print "GAME STARTED!"
print new_game._getScore()
moves = [ (1,'0'),(1,'1,1'), (1,'3,3'), (1,'6,4'), 
        (1,'4,4'), (1,'3,6'), (1, '4,3'), (1, '5,6'), (2,'1,1'), 
        (1,'4,2'), (1, '8,4'), (1, '3,4'),(1,'1,8'), (1, '5,6'),
        (1,'1,2'), (1, '4,8'), (1, '8,2'),(1,'7,8'), (1, '1,4'),
        (1,'3,3'), (1, '3,2'), (1, '7,7'),(1,'1,6'), (1, '1,3'),
        (1,'3,5'), (1, '7,2'), (1, '5,2'),(1,'7,6'), (1, '6,2'),
        (1,'1,7'), (1, '8,7'), (1, '3,8'),(1,'5,7'), (1, '5,8'),
        (1,'7,1'), (1, '5,3'), (1, '7,5')]

for i in moves:
    isvalid, message = new_game._make_move(i[0], i[1])
    print message
    if isvalid:
        print new_game._getScore()
        print "Game mode is:", new_game.game_mode
        if new_game.game_mode=="SINGLE PLAYER":
            print "Calling CPU for move..."
            message = new_game._cpu_move()
            print message
            print new_game._getScore()

