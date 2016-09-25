import endpoints
from protorpc import remote, messages, message_types
from datetime import datetime
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from utils import load_game_logic,\
        update_game_logic, get_by_game_id,\
        update_score_difference_ave
from othello_models import SimpleMessage
from models import User
from othello_models import OthelloGame,\
        OthelloScoreBoardEntry, OthelloGameHistory,\
        OthelloPlayer
from othello_models import NewGameForm, OthelloGameForm,\
    OthelloGameForms, OthelloGameHistoryForm, OthelloHighScoreForm,\
    OthelloHighScoreEntryForm, OthelloPlayerRankingForm,\
    OthelloPlayerRankingFormEntry

import api_common
import json
from othello_logic import OthelloLogic
from othello_models import OthelloDatastoreLogic

# GLOBAL CONSTANTS
SINGLE_PLAYER_MODE = "SINGLE_PLAYER"
TWO_PLAYER_MODE = "TWO_PLAYERS"
DEFAULT_GAME_MODE = SINGLE_PLAYER_MODE
MAX_TOP_SCORERS = 10


# RESOURCE CONTAINERS
GET_USER_GAMES_REQUEST = endpoints.ResourceContainer(
        user_name=messages.StringField(1))
GET_GAME_REQUEST = endpoints.ResourceContainer(
        safe_url=messages.StringField(1),
        game_creator=messages.StringField(2),
        game_id=messages.IntegerField(3),)
GET_GAME_HISTORY_REQUEST = endpoints.ResourceContainer(
        game_id=messages.StringField(1))
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
        user_name=messages.StringField(1),
        game_id=messages.StringField(2),
        safe_url=messages.StringField(3),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
        game_id=messages.StringField(1),
        user_name=messages.StringField(2),
        move=messages.StringField(3),
        safe_url=messages.StringField(4))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@endpoints.api(name='othello',
               version='v0.1')
class OthelloApi(remote.Service):
    """Othello API v0.1"""

    @endpoints.method(api_common.USER_REQUEST,
                      SimpleMessage,
                      path='othellouser',
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
            user_key = ndb.Key(User, request.user_name)
            user = User(key=user_key, name=request.user_name,
                        email=request.email)
            user.put()
            print "Added to User"
        u_key = ndb.Key(User, request.user_name)
        # check if it's OthelloPlayer
        if OthelloPlayer.query(ancestor=u_key).get():
            raise endpoints.ConflictException(
                'An Othello user with that name already exists!')

        # use user_name as key to get game date using creator user_name
        ou_key = ndb.Key(OthelloPlayer, request.user_name, parent=u_key)
        print "Got new key for othello player"
        data = {}
        data['key'] = ou_key
        # adding scoreboard entry
        sc_id = OthelloGame.allocate_ids(size=1, parent=ou_key)[0]
        sc_key = ndb.Key(OthelloScoreBoardEntry, sc_id, parent=ou_key)
        player_score_entry = OthelloScoreBoardEntry(
                key=sc_key,
                points=0,
                wins=0,
                winning_streak=0,
                score_difference_average=0)

        # Adding entities to datastore
        # Added to OthelloPlayer
        OthelloPlayer(**data).put()
        # Added to ScoreBoardEntry
        player_score_entry.put()

        return SimpleMessage(message='User {} created!'.format(
                request.user_name))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(NewGameForm, SimpleMessage,
                      path='newOthelloGame',
                      http_method='POST', name='new_game')
    def new_othello_game(self, request):
        """ Create a new Othello game """
        # check players exist
        for player_name in request.playerNames:
            user_key = ndb.Key(User, player_name)
            user = user_key.get()
            if not user:
                raise endpoints.\
                        NotFoundException('Invalid key'
                                          ', user not found')
            else:
                othello_player = ndb.Key(
                        OthelloPlayer, player_name, parent=user_key).get()
                if not othello_player:
                    raise endpoints.NotFoundException(
                            'Invalid key, othello '
                            'player not found')

        print "Players ok, creating game."
        game_id = self._newOthelloGame(request)

        return SimpleMessage(
                message='New game started. Game id is {}'.format(game_id))

    def _newOthelloGame(self, request):
        """ Logic for creating a new Othello game.
        Create ndb types that will store the game
        logic using the OthelloLogic class
        implementation """

        # set game mode
        if len(request.playerNames) == 1:
            game_mode = SINGLE_PLAYER_MODE
        else:
            game_mode = TWO_PLAYER_MODE

        # get OthelloPlayer keys for this game
        # assert : all keys have been verified to exist
        othello_players_keys = [ndb.Key(
            OthelloPlayer, name, parent=ndb.Key(
                User, name)) for name in request.playerNames]

        # initialize logic
        new_game_logic = OthelloLogic(game_mode=game_mode)
        # initialize game object with
        # explicit array name containers
        json_board = json.dumps(new_game_logic.B)
        json_array_x = json.dumps(new_game_logic.X)
        json_array_y = json.dumps(new_game_logic.Y)
        json_array_n = json.dumps(new_game_logic.N)
        json_array_move = json.dumps(new_game_logic.D)
        json_check_move = json.dumps(new_game_logic.C)
        game_logic = OthelloDatastoreLogic(
                board=json_board,
                player_turn=new_game_logic.CP,
                check_move=json_check_move,
                array_move=json_array_move,
                array_x=json_array_x,
                array_y=json_array_y,
                array_n=json_array_n,
                game_mode=new_game_logic.game_mode)

        new_game = OthelloGame(
                status="ACTIVE",
                starttime=datetime.today(),
                gamelogic=game_logic,
                userKeys=othello_players_keys)

        # link new game to creator, in this case, first user in player list
        g_id = OthelloGame.allocate_ids(size=1,
                                        parent=othello_players_keys[0])[0]
        g_key = ndb.Key('OthelloGame', g_id, parent=othello_players_keys[0])
        new_game.key = g_key
        # add generated id as game id
        new_game.game_id = g_id

        # create game history entity
        # adding scoreboard entry
        new_game.put()
        print "Game created"
        gh_id = OthelloGameHistory.allocate_ids(size=1, parent=g_key)[0]
        gh_key = ndb.Key(OthelloGameHistory, gh_id, parent=g_key)
        game_history = OthelloGameHistory(key=gh_key)

        game_history.put()

        # load OtheloPlayer entities
        players = ndb.get_multi(othello_players_keys)
        for p in players:
            p.gameKeys.append(g_key)
        ndb.put_multi(players)
        print "Added game to player game keys"

        return new_game.game_id

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(GET_GAME_REQUEST, OthelloGameForm,
                      path='getGame', name='get_game', http_method='GET')
    def get_game(self, request):
        """ Gets game status matching safeurl
         or by providing game creator user name and game id"""
        game = get_by_game_id(request.safe_url, request.game_id)
        if not game:
            # search by creator and id
            games = OthelloGame.query()
            for g in games:
            g_key = ndb.Key(User, request.game_creator,
                            OthelloPlayer, request.game_creator,
                            OthelloGame, long(request.game_id))
            game = g_key.get()
        if game:
            return self._copyOthelloGameToForm(game)
        else:
            return OthelloGameForm()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(GET_USER_GAMES_REQUEST, OthelloGameForms,
                      path='getUserGames', name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """ Returns all games where a user is active """
        user_key = ndb.Key(User, request.user_name)
        print "User key", user_key
        player = OthelloPlayer.query(ancestor=user_key).get()
        if not player:
            raise endpoints.NotFoundException(
                    'A User with that name is not registered for Othello!')
        print "Getting games with keys", player.gameKeys
        games = ndb.get_multi(player.gameKeys)
        if not games:
            return OthelloGameForms(message='No games found for ' +
                                    request.user_name)

        # in memory filter for active games
        # instead of querying all active games with user in userKeys
        # it is probably faster to load game keys for user and filter in
        # memory only ACTIVE games.
        if games:
            active_games = [ag for ag in games if ag.status == "ACTIVE"]
        if active_games:
            return OthelloGameForms(
                 othello_games=[self._copyOthelloGameToForm(game)
                                for game in active_games])
        else:
            return OthelloGameForms(message='No active games found for ' +
                                    request.user_name)

    def _copyOthelloGameToForm(self, game):
            game_logic = load_game_logic(game.gamelogic)
            p1, p2 = game_logic._getScore()
            player1 = game.userKeys[0].parent().get().name
            if game_logic.game_mode == TWO_PLAYER_MODE:
                player2 = game.userKeys[1].parent().get().name
            else:
                player2 = None
            return OthelloGameForm(
                    game_id=game.game_id,
                    player_one=player1,
                    player_two=player2,
                    score_p1=p1,
                    score_p2=p2,
                    game_status=game.status,
                    board=game.gamelogic.board,
                    game_mode=game.gamelogic.game_mode)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(MAKE_MOVE_REQUEST, SimpleMessage,
                      path='makeMove', name='make_move', http_method='POST')
    def make_move(self, request):
        """ Make a move for a game following the rules of Othello """

        isvalid, message = self._make_move(request)
        return SimpleMessage(message=message)

    # @ndb.transactional(xg=True)
    def _make_move(self, request):
        """ Controller for movements. If game is SINGLE_PLAYER,
        CPU will take turn after player submits valid move.
        Otherwise, CPU waits for valid move or yield from player"""
        game = get_by_game_id(request.safe_url, request.game_id)
        if not game:
            return False, "Game not found"
        print "Game status", game.status, type(game.status)
        if not game.status == "ACTIVE":
            return False, "This game is not active"

        if ndb.Key(OthelloPlayer, request.user_name,
                   parent=ndb.Key(User, request.user_name))\
                not in game.userKeys:
            return False, "Player {0} is not registered for this game".\
                    format(request.user_name)
        parent_keys = [p.parent() for p in game.userKeys]
        players = ndb.get_multi(parent_keys)
        print "Players in this game", players

        # load game logic object
        game_logic = load_game_logic(game.gamelogic)

        player_turn = 1 if players[0].name == request.user_name else 2
        isvalid, message = game_logic._make_move(player_turn, request.move)
        print message

        # load an update game history in memory
        game_history = OthelloGameHistory.query(ancestor=game.key).get()
        if not game_history.moves:
            moves = []
        else:
            moves = json.loads(game_history.moves)
        # append moves from user if move is valid
        if isvalid:
            moves.append([request.user_name, request.move])
            if game_logic.game_mode == TWO_PLAYER_MODE:
                # PUSH TASK QUEUE to notify opponent that move has been made
                taskqueue.add(params={'email': players[0].email if
                              player_turn == 2 else players[1].email,
                              'score': game_logic._getScore()},
                              url='/tasks/send_gameturn_notification_email')

        print "Whose turn is it?", game_logic.CP
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # CPU MOVE

        if isvalid and game_logic.game_mode == SINGLE_PLAYER_MODE:
            print "Calling CPU for move..."
            isvalid, cpu_move = game_logic._cpu_move()
            moves.append(['cpu', cpu_move])
            print message
            message = "Your move was valid. {0}".format(cpu_move)

        # updates game logic with values from OthelloLogic instance
        update_game_logic(game_logic, game.gamelogic)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GAME OVER CONDITIONS

        if game_logic._isBoardFull():
            game.status = "ENDED_COMPLETE"
            message = "Game has ended. The board is full!"
        if request.move == '0':
            game.status = "ENDED_INCOMPLETE"
            message = "The user abandoned the game. "
            "Score will be accounted for"

        if not game.status == "ACTIVE":
            # get score
            score_player1, score_player2 = game_logic._getScore()
            score_diff = abs(score_player1-score_player2)
            player1_entry = OthelloScoreBoardEntry.query(
                    ancestor=game.userKeys[0]).get()
            # CHECK END OF TWO PLAYER GAME
            if game_logic.game_mode == TWO_PLAYER_MODE:
                player2_entry = OthelloScoreBoardEntry.query(
                        ancestor=game.userKeys[1]).get()
                if score_player1 > score_player2:
                    # PLAYER 1 WINS
                    message = "Player {0} wins!".format(
                            game.userKeys[0].parent().get().name)
                    player1_entry.points += score_player1
                    player1_entry.wins += 1
                    player1_entry.winning_streak += 1
                    # update score difference average - player 1
                    update_score_difference_ave(
                            player1_entry.score_difference_average,
                            score_diff)
                    player2_entry.winning_streak = 0
                elif score_player1 < score_player2:
                    # PLAYER 2 WINS
                    message = "Player {0} wins!".format(
                            game.userKeys[1].parent().get().name)
                    player2_entry.points += score_player2
                    player2_entry.wins += 1
                    player2_entry.winning_streak += 1
                    # update score difference average - player 2
                    update_score_difference_ave(
                            player2_entry.score_difference_average,
                            score_diff)
                    player1_entry.winning_streak = 0
                else:
                    # tie game
                    message = "This game is tied! No changes in scoreboard"
                # update players scoreboard entries in datastore
                ndb.put_multi([player1_entry, player2_entry])
            # CHECK END FOR SINGLE PLAYER GAME
            if game_logic.game_mode == SINGLE_PLAYER_MODE:
                if score_player1 > score_player2:
                    # PLAYER 1 WINS
                    message = "Player {0} wins!".format(
                            game.userKeys[0].parent().get().name)
                    player1_entry.points += score_player1
                    player1_entry.wins += 1
                    update_score_difference_ave(
                            player1_entry.score_difference_average,
                            score_diff)
                    player1_entry.winning_streak += 1
                elif score_player1 < score_player2:
                    message = "CPU wins."
                    player1_entry.winning_streak = 0
                player1_entry.put()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # UPDATE GAME AND HISTORY DATASTORE
        game.put()
        # UPDATE GAME HISTORY
        game_history.moves = json.dumps(moves)
        game_history.put()

        return True, message

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(CANCEL_GAME_REQUEST, SimpleMessage,
                      path='cancelGame', name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        """ Cancel game. Game state and history is preserved in datastore.
        Only requestor of game (parent) can cancel it"""

        # try to get game by safe_url or by game_id
        game = get_by_game_id(request.safe_url, request.game_id)

        if not game:
            # try to find game with parent key and entity id
            op = OthelloPlayer.query(
                    ancestor=ndb.Key(User, request.user_name)).get()
            k = ndb.Key(OthelloGame, long(request.game_id),
                        parent=op.key)
            game = k.get()

        if not game:
            # game cannot be found
            raise endpoints.NotFoundException('Game not found!')

        if game.status == "CANCELLED":
            raise endpoints.BadRequestException('Game has already been'
                                                ' cancelled.')
        if game and (game.key.parent() != OthelloPlayer.query(
                    ancestor=ndb.Key(User, request.user_name)).get().key):
            raise endpoints.BadRequestException('User is not game'
                                                ' creator')

        # cancel game
        game.status = "CANCELLED"
        game.put()

        return SimpleMessage(message='Found and cancelled Othello game.')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(message_types.VoidMessage, OthelloHighScoreForm,
                      path='getHighScores', name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """ Get top MAX_TOP_SCORERS high scores from all users,
        sorted by score, descending """
        scores = OthelloScoreBoardEntry.query()
        if scores.count() > 0:
            print 'Found some scores', scores
            for i in scores:
                print "score:", i
            scores = scores.order(-OthelloScoreBoardEntry.wins)
            scores = scores.order(-OthelloScoreBoardEntry.points)
            scores = scores.fetch(MAX_TOP_SCORERS)
            return OthelloHighScoreForm(
                    message="Top {0} scores".format(MAX_TOP_SCORERS),
                    scoreboardentry=[self._copyHighScoreEntryToForm(
                        hse) for hse in scores])
        else:
            return OthelloHighScoreForm(
                message='No scores yet! Play some games.')

    def _copyHighScoreEntryToForm(self, high_score_entry):
            return OthelloHighScoreEntryForm(
                player=high_score_entry.key.parent().parent().get().name,
                points=high_score_entry.points,
                wins=high_score_entry.wins,
                winning_streak=high_score_entry.winning_streak)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(message_types.VoidMessage, OthelloPlayerRankingForm,
                      path='getUserRankings', name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """ User ranking based on the sum of wins + winning streak +
        average win score difference / 10 """

        ranking = OthelloScoreBoardEntry.query()
        if ranking.count() > 0:
            print 'Found some ranked users'
            ranking = ranking.order(-OthelloScoreBoardEntry.performance_index)
            ranking = ranking.fetch(MAX_TOP_SCORERS)
            return OthelloPlayerRankingForm(
                    entries=[self._copyRankingEntryToForm(
                        ref) for ref in ranking],
                    explanation='This ranking is computed as the sum of'
                    ' winning streak + games won + '
                    'winning score difference average / 10')
        else:
            return OthelloPlayerRankingForm(
                explanation='No rankings available yet! Play some games.')

    def _copyRankingEntryToForm(self, ranking_entry):
        return OthelloPlayerRankingFormEntry(
            player=ranking_entry.key.parent().parent().get().name,
            winning_streak=ranking_entry.winning_streak,
            average_point_difference=ranking_entry.score_difference_average,
            performance_index=ranking_entry.performance_index)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(GET_GAME_HISTORY_REQUEST, OthelloGameHistoryForm,
                      path='getGameHistory',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """ Query game history kind for games matching id """
        game = get_by_game_id(safe_url=None, game_id=request.game_id)
        if not game:
            return OthelloGameHistoryForm(
                    message='No history found for game ' + request.game_id)
        # query Othello game history entity with game id request.game_id
        game_history = OthelloGameHistory.query(ancestor=game.key).get()
        if not game_history:
            raise endpoints.BadRequestException(
                    'Could not find history linked to this game')

        return OthelloGameHistoryForm(
                message="Found game history",
                game_id=int(request.game_id),
                moves=game_history.moves)
