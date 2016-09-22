from datetime import date
import endpoints
from protorpc import remote, messages

GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                                   email=messages.StringField(2))
