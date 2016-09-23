import logging
import endpoints
from protorpc import remote, messages, message_types
from datetime import datetime
from google.appengine.api import memcache
#from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from utils import get_by_urlsafe, load_game_logic,\
        update_game_logic
from othello_models import SimpleMessage
from models import User
from othello_models import OthelloGame, OthelloScoreBoard,\
    OthelloGameHistory, OthelloPlayer
from othello_models import NewGameForm

import api_common
import json
from othello_logic import OthelloLogic
from othello_models import OthelloDatastoreLogic

DEFAULT_GAME_MODE="SINGLE_PLAYER"
GET_USER_GAMES_REQUEST = endpoints.ResourceContainer(
        user_name=messages.StringField(1))
MAX_TOP_SCORERS = 10
GET_GAME_REQUEST = endpoints.ResourceContainer(
        safe_url=messages.StringField(1),
        game_id=messages.StringField(2),)
GET_GAME_HISTORY_REQUEST = endpoints.ResourceContainer(
        game_id = messages.StringField(1))
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
        user_name=messages.StringField(1),
        game_id=messages.StringField(2),
        safe_url=messages.StringField(3),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
        game_id=messages.StringField(1),
        user_name=messages.StringField(2),
        move=messages.StringField(3),
        safe_url=messages.StringField(4))


@endpoints.api( name='othello',
                version='v0.1')
class OthelloApi(remote.Service):
    """Othello API v0.1"""

    @endpoints.method(api_common.USER_REQUEST,
                      SimpleMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create an OthelloPlayer using User model as ancestor.
        An entity for Othello user is created to keep track of 
        games keys"""

        # call transactional add user on User and OthelloPlayer
        return self._createOthelloPlayerObject(request)
    
    # @ndb.transactional()
    # Only ancestory queries are allowed inside transactions
    def _createOthelloPlayerObject(self, request):
        if User.query(User.name == request.user_name).get():
            print "Found in User"
        else:
            # user not found, adding both to User
            user = User(name=request.user_name, email=request.email)
            user.put()
            print "Added to User"
        u_key = ndb.Key(User, request.user_name)
        # check if it's OthelloPlayer
        if OthelloPlayer.query(ancestor=u_key).get():
            raise endpoints.ConflictException(
                'An Othello user with that name already exists!')        
        ou_id = OthelloPlayer.allocate_ids(size=1, parent=u_key)[0]
        ou_key = ndb.Key(OthelloPlayer, ou_id, parent=u_key)
        print "Got new key for othello player"
        data = {}
        data['key'] = ou_key
        print "Adding object to datastore"
        OthelloPlayer(**data).put()
        print "Added to OthelloPlayer"

        return SimpleMessage(message='User {} created!'.format(
                request.user_name))


    @endpoints.method(message_types.VoidMessage,SimpleMessage,
            path="othelloTest",
            http_method='GET', name='othelloTest')
    def othelloTest(self,request):
        """ Dummy test to check API """
        return (SimpleMessage(message="Added to API."))


    @endpoints.method(NewGameForm, SimpleMessage,
            path='newOthelloGame',
            http_method='POST', name='new_game')
    def new_othello_game(self, request):
        """ Create a new Othello game """ 
        # print input 
        players = []
        for i in request.playerNames:
            # print check users exist
            if not ndb.Key(User, i):
                raise endpoints.BadRequestException('Invalid key')
            print i
        print "Players ok, creating game."
        
        self._newOthelloGame(request)

        return SimpleMessage(message='New game started,')

    def _newOthelloGame(self, request):
        """ Logic for creating a new Othello game. 
        Create an 8x8 board and assign game key to
        OthelloPlayer entities. TODO: By default, first user
        in list will be ancestor of OthelloGame. This can be
        improved by adding oauth. """
        

        # set game mode
        if len(request.playerNames) == 1:
            game_mode = DEFAULT_GAME_MODE
        else:
            game_mode = "TWO_PLAYERS"

        # get OthelloPlayer keys for this game
        user_keys = [ndb.Key(User, i) for i in request.playerNames]
        othello_player_keys = [ OthelloPlayer.query(ancestor=uk).\
                get().key for uk \
                in user_keys ]

        # initialize logic 
        new_game_logic = OthelloLogic(game_mode=game_mode)
        # initialize game object
        # explicit array name containers, to avoid ambiguities if 
        # using repated=True keyword
        json_board = json.dumps(new_game_logic.B)
        json_array_x = json.dumps(new_game_logic.X)
        json_array_y = json.dumps(new_game_logic.Y)
        json_array_n = json.dumps(new_game_logic.N)
        json_array_move = json.dumps(new_game_logic.D)
        json_check_move = json.dumps(new_game_logic.C)
        game_logic = OthelloDatastoreLogic(board=json_board,
                player_turn=new_game_logic.CP,
                check_move=json_check_move,
                array_move=json_array_move,
                array_x=json_array_x,
                array_y=json_array_y,
                array_n=json_array_n,
                game_mode=new_game_logic.game_mode)

        new_game = OthelloGame(status = "ACTIVE", starttime = datetime.today(), 
                gamelogic = game_logic, userKeys = othello_player_keys)

        #link new game to creator, in this case, first user in player list
        g_id = OthelloGame.allocate_ids(size=1, parent=othello_player_keys[0])[0]
        g_key = ndb.Key('OthelloGame', g_id, parent=othello_player_keys[0])
        new_game.key = g_key

        new_game.put()
        print "Game created"
        #print "memcaching game"
        #memcache(key='testdata', value=new_game, time=3600)
        #print "game added to memcache. need to be checkd for every read operation"
        
        players = ndb.get_multi(othello_player_keys)
        for p in players:
            p.gameKeys.append(g_key)
        ndb.put_multi(players)


        print "Added game to player game keys"

    @endpoints.method(GET_GAME_REQUEST, SimpleMessage,
            path='getGame', name='get_game', http_method='GET')
    def get_game(self, request):
        """ Gets game status matching safeurl """
        if not request.game_id:
            game = get_by_urlsafe(request.safe_url, OthelloGame)
        else:
            g_key = ndb.Key(OthelloGame, int(request.game_id))
            game = g_key.get()
        if game:
            board = json.loads(game.gamelogic.board)
            return SimpleMessage(message="Here is the game board" + str(board))
        else:
            return SimpleMessage(message='No game found')


    @endpoints.method(GET_USER_GAMES_REQUEST, SimpleMessage,
            path='getUserGames',name='get_user_games',http_method='GET')
    def get_user_games(self, request):
        """Returns all games where a user is active, including
        two player games""" 
        user_key = ndb.Key(User, request.user_name)
        print "User key", user_key
        player = OthelloPlayer.query(ancestor=user_key).get()
        if not player:
            raise endpoints.NotFoundException(
                    'A User with that name is not registered for Othello!')
        print "Getting games with keys", player.gameKeys
        games = ndb.get_multi(player.gameKeys)

        # in memory filter for active games
        # instead of querying all active games with user in userKeys
        # it is probably faster to load game keys for user and filter in 
        # memory only ACTIVE games.
        active_games = [ ag for ag in games if ag.status == "ACTIVE" ]

        if len(active_games) > 0:
            return (SimpleMessage(message=str(active_games)))
        return (SimpleMessage(message='No games found for ' + request.user_name))

    
    @endpoints.method(MAKE_MOVE_REQUEST, SimpleMessage,
            path='makeMove', name='make_move', http_method='POST')
    def make_move(self, request):
        """ Make a move for a game following the rules of Othello """

        #make transactional call to make move
        isvalid, message = self._make_move(request)
        if isvalid:
            return SimpleMessage(message="Move has been made, score is TBC.")
        else:
            return SimpleMessage(message="The move was not allowed")


    @ndb.transactional
    def _make_move(self, request):
        """ Required for two player games, so game state is consistent with
        #might not be able to get with id only, probably needs parent key
        player moves"""
        #game = ndb.Key(OthelloGame, long(request.game_id)).get()
        game = get_by_urlsafe(request.safe_url,OthelloGame)
        if not game:
            return SimpleMessage(messages="Game not found")
        players = [ p.key.parent.get() for p  in game.userKeys ]
        print "Players in this game", players
        if request.name not in players:
            return False, "Player {0} is not registered for this game".\
                    format(request.user_name)
        game_logic=load_game_logic(game.gamelogic)
        player_number = request.user_name.index[request.user_name] + 1
        isvalid, message = game_logic._make_move(1,request.move)
        print "Whose turn is it?", game_logic.CP
        print message
        print "game mode:", game_logic.game_mode
        if isvalid and game_logic.game_mode == DEFAULT_GAME_MODE:
            print "Calling CPU for move..."
            isvalid, message =  game_logic._cpu_move()
            print message
        update_game_logic(game_logic, game.gamelogic)
        game_logic._getScore()
        game.put()
        #update datastore with game snapshot

        return isvalid, message
        #if othello_logic._make_move(board, request.user_name, request.move):
            #update game board
        #    score = othello_logic._getScore(board)
        #    game.board = json.dumps(board)
        #    game.put()
        #    return True
        #return False


    @endpoints.method(CANCEL_GAME_REQUEST, SimpleMessage,
            path='cancelGame', name='cancel_game', http_method='POST')
    def cancel_game(self, request):
        """ Cancel and remove game from datastore.
        Only requestor of game (parent) can cancel it"""

        if request.safe_url:
            game = get_by_urlsafe(request.safe_url, OthelloGame)
            if game and game.status == "CANCELLED":
                raise endpoints.BadRequestException('Game has already been'
                     ' cancelled.')
            if game and (game.key.parent() != OthelloPlayer.query(
                    ancestor=ndb.Key(User, request.user_name)).get().key) :
                raise endpoints.BadRequestException('User is not game'
                        ' creator')
        else:
            op = OthelloPlayer.query(ancestor=ndb.Key(User, request.user_name)).get()
            k = ndb.Key(OthelloGame, long(request.game_id), 
                    parent=op.key)
            game = k.get()
        #MyModel.get_by_id(key.id(), parent=key.parent(), app=key.app(), namespace=key.namespace())
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        if game.status == "CANCELLED":
            raise endpoints.BadRequestException('Game has already been'
                    ' cancelled.')
        # cancel game        
        game.status = "CANCELLED"
        game.put()
        
        return SimpleMessage(message='Found and cancelled Othello game.')
        

    @endpoints.method(message_types.VoidMessage, SimpleMessage,
            path='getHighScores', name='get_high_scores', http_method='GET')
    def get_high_scores(self, request):
        """ Get top MAX_TOP_SCORERS high scores from all users, 
        sorted by score, descending """
        scores = OthelloScoreBoard.query()
        if scores.count() > 0:
            print 'Found some scores', scores
            for i in scores:
                print "score:", i
            scores = scores.order(-OthelloScoreBoard.points)
            scores = scores.fetch(MAX_TOP_SCORERS)
        else:
            return SimpleMessage(message='No scores yet! Play some games.')
        return SimpleMessage(message='Found scores?')

    @endpoints.method(message_types.VoidMessage, SimpleMessage,
            path='getUserRankings', name='get_user_rankings', http_method='GET')
    def get_user_rankings(self,request):
        """ User ranking based on winning streaks, i.e. consecutive matches won """
        ranking = OthelloScoreBoard.query()
        if ranking.count() > 0:
            print 'Found some ranked users'
            ranking = q.order(-OthelloScoreBoard.winning_streak)
            ranking = q.fetch(MAX_TOP_SCORERS)
        else:
            return SimpleMessage(message='No rankings available yet! Play some games.')
        return SimpleMessage(message='Rankings available, tbc...')
    
    
    @endpoints.method(GET_GAME_HISTORY_REQUEST, SimpleMessage,
           path='getGameHistory', name='get_game_history', http_method='GET')
    def get_game_history(self, request):
        """ Query game history kind for games matching id """
        moves = OthelloGameHistory.query(ancestor=ndb.Key(OthelloGame, request.game_id))
        if moves.count() > 0 :
            return SimpleMessage(message='Found game history, tbc...')
        else:
            return SimpleMessage(message='No history found for game ' + request.game_id)
