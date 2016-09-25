"""utils.py - File for collecting general utility functions."""
from google.appengine.ext import ndb
import endpoints
from othello_logic import OthelloLogic
from othello_models import OthelloGame
import json


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def get_by_game_id(safe_url, game_id):
    """ This is to find a game entity by an assigned game_id """
    """ if no game is found None is returned """
    if safe_url:
        game = get_by_urlsafe(safe_url, OthelloGame)
    elif game_id:
        games = OthelloGame.query().fetch()
        if games:
            game = [g for g in games if g.game_id == int(game_id)]
            print "GAME:", game
            if game:
                return game[0]
    return game


def load_game_logic(game_entity):
    game_logic = OthelloLogic()
    game_logic.game_mode = game_entity.game_mode
    game_logic.B = json.loads(game_entity.board)
    game_logic.CP = game_entity.player_turn
    game_logic.C = json.loads(game_entity.check_move)
    game_logic.N = json.loads(game_entity.array_n)
    game_logic.X = json.loads(game_entity.array_x)
    game_logic.Y = json.loads(game_entity.array_y)
    game_logic.D = json.loads(game_entity.array_move)
    return game_logic


def update_game_logic(game_logic, game_datastore_logic):
    # prepare json
    json_board = json.dumps(game_logic.B)
    json_array_x = json.dumps(game_logic.X)
    json_array_y = json.dumps(game_logic.Y)
    json_array_n = json.dumps(game_logic.N)
    json_array_move = json.dumps(game_logic.D)
    json_check_move = json.dumps(game_logic.C)
    # load into datastore object
    game_datastore_logic.board = json_board
    game_datastore_logic.player_turn = game_logic.CP
    game_datastore_logic.check_move = json_check_move
    game_datastore_logic.array_move = json_array_move
    game_datastore_logic.array_x = json_array_x
    game_datastore_logic.array_y = json_array_y
    game_datastore_logic.array_n = json_array_n
    game_datastore_logic.game_mode = game_logic.game_mode


def update_score_difference_ave(score_difference_average,
                                score_difference):
    if not score_difference_average:
        score_difference_average = score_difference
    else:
        score_difference_average += score_difference
        score_difference_average /= 2
