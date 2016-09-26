#!/usr/bin/env python
from protorpc import messages
from google.appengine.ext import ndb


class SimpleMessage(messages.Message):
    message = messages.StringField(1)


class NewGameForm(messages.Message):
#    playerNames = messages.StringField(1,
#            repeated=True)
    player_one = messages.StringField(1,
            required=True)
    player_two = messages.StringField(2)
     

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class OthelloPlayer(ndb.Model):
    gameKeys = ndb.KeyProperty(repeated=True, kind='OthelloGame')


class OthelloDatastoreLogic(ndb.Model):
    board = ndb.JsonProperty()
    player_turn = ndb.IntegerProperty()
    check_move = ndb.JsonProperty()
    array_move = ndb.JsonProperty()
    array_x = ndb.JsonProperty()
    array_y = ndb.JsonProperty()
    array_n = ndb.JsonProperty()
    game_mode = ndb.StringProperty()


class OthelloGame(ndb.Model):
    """ OthelloGame object """
    game_id = ndb.IntegerProperty()
    status = ndb.StringProperty()
    starttime = ndb.DateProperty()
    userKeys = ndb.KeyProperty(repeated=True, kind='OthelloPlayer')
    gamelogic = ndb.StructuredProperty(OthelloDatastoreLogic)


class OthelloGameHistory(ndb.Model):
    moves = ndb.JsonProperty()


class OthelloScoreBoardEntry(ndb.Model):
    """ Othello score for a player accounted for  completed
    or abandoned games. Used for both high scores
    and rankings """
    points = ndb.IntegerProperty(required=True)
    wins = ndb.IntegerProperty(required=True)
    winning_streak = ndb.IntegerProperty(required=True)
    score_difference_average = ndb.FloatProperty(required=True)
    performance_index = ndb.ComputedProperty(
            lambda self: self.winning_streak + self.wins +
            (self.score_difference_average/10))


class OthelloGameForm(messages.Message):
    """ Othello game informtion """
    game_id = messages.IntegerField(1)
    player_one = messages.StringField(2)
    player_two = messages.StringField(3)
    score_p1 = messages.IntegerField(4)
    score_p2 = messages.IntegerField(5)
    game_status = messages.StringField(6)
    board = messages.StringField(7)
    game_mode = messages.StringField(8)


class OthelloGameForms(messages.Message):
    """ Container reponse for multiple Othello games """
    othello_games = messages.\
        MessageField(OthelloGameForm,
                     1, repeated=True)
    message = messages.StringField(2)


class OthelloGameHistoryForm(messages.Message):
    """ Othello game history """
    game_id = messages.IntegerField(1)
    moves = messages.StringField(2)
    game_status = messages.StringField(3)


class OthelloHighScoreEntryForm(messages.Message):
    """ Othello score board entry """
    player = messages.StringField(1)
    points = messages.IntegerField(2)
    wins = messages.IntegerField(3)
    winning_streak = messages.IntegerField(4)


class OthelloHighScoreForm(messages.Message):
    """ Othello MAX_TOP_SCORERS board """
    scoreboardentry = messages.MessageField(
        OthelloHighScoreEntryForm, 1, repeated=True)
    message = messages.StringField(2)


class OthelloPlayerRankingFormEntry(messages.Message):
    """ Othello player rankings form """
    player = messages.StringField(1)
    winning_streak = messages.IntegerField(2)
    average_point_difference = messages.FloatField(3)
    performance_index = messages.FloatField(4)


class OthelloPlayerRankingForm(messages.Message):
    explanation = messages.StringField(1)
    entries = messages.MessageField(
            OthelloPlayerRankingFormEntry, 2,
            repeated=True)
