#!/usr/bin/env python
__author__ = 'manuel.aguilar.alvarez@google.com (Manuel Aguilar)'

import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb
from models import User

class SimpleMessage(messages.Message):
    message = messages.StringField(1)

class NewGameForm(messages.Message):
    playerNames = messages.StringField(1, repeated=True)

class OthelloPlayer(ndb.Model):
    gameKeys = ndb.KeyProperty(repeated=True, kind='OthelloGame')


class OthelloGame(ndb.Model):
    """ OthelloGame object """
    status = ndb.StringProperty()
    starttime = ndb.DateProperty()
    board = ndb.JsonProperty()
    userKeys = ndb.KeyProperty(repeated=True, kind='OthelloPlayer')
    gamelogic = ndb.BlobProperty()


class OthelloGameHistory(ndb.Model):
    moves = ndb.JsonProperty()
    #game = ndb.KeyProperty(required=True, kind='OthelloGame')


class OthelloScoreBoard(ndb.Model):
    """ Othello score for a player accounted for  completed
    games """
    #user = ndb.KeyProperty(required=True, kind='User')
    points = ndb.IntegerProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')
    winning_streak = ndb.IntegerProperty(required=True)

