import endpoints
from protorpc import remote, messages

# SHARED REQUEST RESOURCES FOR DEMO API AND OTHELLO API

GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(
        user_name=messages.StringField(1,required=True), email=messages.StringField(2))
