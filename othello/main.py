#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import GuessANumberApi
from othello import OthelloGame, OthelloPlayer
from models import User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            subject = 'This is a reminder!'
            body = 'Hello {}, try out Guess A Number!'.format(user.name)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


class UpdateAverageMovesRemaining(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        GuessANumberApi._cache_average_attempts()
        self.response.set_status(204)


class SendActiveGameReminderEmail(webapp2.RequestHandler):
    def get(self):
        """ Send a daily reminder to all users with active games """
        app_id = app_identity.get_application_id()
        active_games = OthelloGame.query(OthelloGame.status == "ACTIVE")
        subject = 'You have an active game of Othello in app engine!'
        body = 'Hello {0}, you have a game identified with {1} that is '
        'waiting for your next move!'
        for active_game in active_games:
            for player_key in active_game.userKeys:
                print player_key
                player = player_key.parent().get()
                player_name = player.name
                player_email = player.email
                # adds game id from OthelloGame and user name from User
                body.format(active_game.game_id, player_name)
                mail.send_mail('noreply@{0}.appspotmail.com'.format(app_id),
                               player_email,
                               subject,
                               body)


class SendGameTurnOpponentEmail(webapp2.RequestHandler):
    def post(self):
        """ Send an email to opponent's turn in TWO GAME PLAYER """
        app_id = app_identity.get_application_id()
        mail.send_mail(
                'noreply@{0}.appspotmail.com'.format(app_id),
                self.request.get('email'),
                'Game notification - Your Othello game move',
                'Your opponent made a move! The score is'
                ' {0}, it is your turn to make a move.'.
                format(self.request.get('score'))
                        )


app = webapp2.WSGIApplication([
    ('/crons/send_active_game_reminder', SendActiveGameReminderEmail),
    ('/tasks/send_gameturn_notification_email', SendGameTurnOpponentEmail),
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
