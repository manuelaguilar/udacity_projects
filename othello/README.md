#Othello C64 for App Engine 

## Set-Up Instructions:
1. This app is hooked to the same api server where the demo game was provided.
 The demo app was slightly modified to use a few common resource containers, which
were moved to a common file. Also, the entity design reuses the content of the 
User kind, suggesting that other games can be hooked to the api server in the same way
(See end of api.py file).

1. To set it up, add the application to your local dev app engine, and modify the 
project id.

1. The setup sequence is:
  - Start application
  - Add some users via the Othello API. This will add them to the User kind of they are
not already there.
  - Start a game, either single or multiplayer. For ease of use, I added a game id property.
You can retrieve game ids by using the get_user_games endpoint.
  - To make a move, enter game id, user id, and movement coordinates in format row,col. The application
will detect if the user is in the game and if it's his or her turn. There is no check on
the move input, so make sure it's row,col. There are two additional moves. Move 0 will
make the current player abdicate from the game and give the opponent a win. 
Move 9 will yield the turn to the other player, either CPU or the other player. It is
possible that too many yields will remove all opponents pieces, for which the game would
have to be abandoned or cancelled. The algorithm doesn't detect for no more user moves
possible, so a user will have to decide when to yield or when to end the game, provided
the board is not completely filled in yet (game over!).
  - Moves will return a message and the CPU will make an immediate move if in SINGLE PLAYER MODE.
  - To view the status of the game board, you have to use either get_game or get_user_games.
Another way to see the plays is by looking at the application standard output. I added a 
pretty print for the 8x8 matrix so it's easier to play using the App Engine API web client,
and the GoogleAppEngineLauncher log screen.
 
##Game Description:
Othello C64 is a port from an old Spanish magazine, which was originally implemented in 
BASIC.
The game is set in an 8x8 board, where the players, red and yellow teams, attempt to flank
and colonize each other's pieces with every move. The board is originally set with 4 pieces
on the center of the board (rows 4 and 5, columns 4 and 5, one opposing piece next to each
other).
A valid move consists on placing a player piece flanking as many pieces from the opponent
on both ends, in any direction. The opponent's piece or pieces have to be aligned
consecutively with no spaces in between. Note that a move can result in multiple alignments
which gives the most gains to towards victory. Each player takes one turn.
A player can yield its turn to the other player if he or she cannot move (the CPU does this).
Once the board is filled with player's pieces, the game ends and the total are computed.
The player with the most pieces wins. There is also the possibility of a tie.
Any of the players can abandon the game at any time, which is different to the 'cancel' game
feature that just freezes the game with no player stats computed.

##Files Included:
 - othello.py: Contains endpoints for the Othello game.
 - othello_gamelogic.py: Contains the whole logic of the game following its original
implementation as a tribute to the old Commodore 64.
 - othello_logic_testdriver.py: a script to test the game logic with a complete game.
 - othello_models.py: Entity and message definitions for the Othello game app.
 - api.py: Endpoints and logic of guess a number demo app.
 - app.yaml: App configuration, including task and cron job in project scope.
 - cron.yaml: Cronjob configuration, including schedule for job in project scope.
 - main.py: Handlers for tasks and cron jobs, including cronjob and task in project scope.
 - models.py: Entity and message definitions for demo app.
 - utils.py: Helper functions, including get entity, get game by id, conversion of game
logic json objects into arrays and some arithmetic to obtain game difference points.

##Endpoints Included:
 - **create_user**
    - Path: 'othellouser'
    - Method: POST
    - Parameters: user_name, email
    - Returns: Message confirming creation of a user for Othello.
    - Description: Creates a new User if no one found. If User is found an entry 
    is created for OthelloUser, which holds the keys to Othello games. Othello 
    player is added to the scoreboard. It will raise a ConflictException if a User 
    with that user name already exists.
    
 - **new_game**
    - Path: 'newOthelloGame'
    - Method: POST
    - Parameters: user_name (1 or 2)
    - Returns: Message confirming game started. Game info is meant to be retrieved
    with provided user id in message.
    - Description: Creates a new Game, in single or two player mode depending on how
    many users were added to request. Game logic, and game history are initialized 
    for player(s) in game. user_name(s) provided must correspond to an
    existing user, otherwise it will raise a NotFoundException.
     
 - **get_game**
    - Path: 'getGame'
    - Method: GET
    - Parameters: safe_url, game_id, creator_name
    - Returns: OthelloGameForm with current game state.
    - Description: Returns the current state of an Othello game. Endpoint can either
    search directly with safe_url, with game id, which is provided when game is 
    created, or with a combination of creator user name and game id.
    
 - **get_user_games**
    - Path: 'getUserGames'
    - Method: GET
    - Parameters: user name.
    - Returns: OthelloGameForms presenting game information for all user's active
    games.
    - Description: Returns a game description, including the game board for all
    active games for a given user.

 - **make_move**
    - Path: 'makeMove'
    - Method: POST
    - Parameters: game_id, user_name, move, safe_url
    - Returns: A message indicating the if a move was valid, or invalid. Returns 
    coordinates of move from CPU when in SINGLE PLAYER MODE.
    - Description: Takes a pair of row, column coordinates in x,y form, or a single
    digi, 0 for abandoning a game or 9 to yield turn to the opponent.
    API user must ensure input is properly entered. A message will be returned giving
    information if the move was successful, give a reason if it wasn't, and will
    have the CPU move coordinates in case of a single player game. If the board
    is filled to 64 pieces, the game ends.

 - **cancel_game**
    - Path: 'cancelGame'
    - Method: POST
    - Parameters: user_name, game_id, safe_url
    - Returns: Message indicating game was cancelled.
    - Description: The game will be set to status CANCELLED, but the game state will
    be kept. It raises NotFound exception is game can't be found, or a BadRequest
    exception if the game has been already cancelled.
    
 - **get_high_scores**
    - Path: 'getHighScores'
    - Method: GET
    - Parameters: None
    - Returns: OthelloHighScoreForm
    - Description: Returns top 10 scores ordered by wins, and then by points. If there
    are no games yet, it returns a message inviting to play some games.
    
 - **get_user_rankings**
    - Path: 'getUserRankings'
    - Method: GET
    - Parameters: None
    - Returns: OthelloPlayerRankingForm 
    - Description: Returns top 10 ranked users based on a specific criteria: 
    wins + winning streak + (average winning game score differential / 10)

  - **get_game_history**
    - Path: 'getGameHistory'
    - Method: GET
    - Parameters: game_id
    - Returns: OthelloGameHistory form containinglist of moves for a specific game_id.
    - Description: It returns the game history for a game. If no game is found
    it returns a message indicating the game id doesn't give results. If a game 
    is found but there is no game history linked to it, a BadRequest exception 
    is raised.
    
##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address. 

 - **OthelloPlayer**
    - Child of User. Contains Othello game keys associated to a User.
    
 - **OthelloGame**
    - Child of OthelloPlayer game creator. Contains game id, status, starttime,
    OthelloPlayer user keys, and OthelloDatastoreLogic (game state). 
  
 - **OthelloDatastoreLogic**
    - Stores data maps to the OthelloLogic class. From here, this class is 
    instantiated every time the user makes a move.

 - **OthelloGameHistory**
    - Child of OthelloGame. Stores game moves for a unique OthelloGame.

 - **OthelloScoreBoardEntry**
    - Child of OthelloPlayer. Stores game stats, including points, wins, winning streak,
    score difference average and the ComputedProperty performance_index, which is 
    updated every time a game ends, using the values of wins, winning_streak, and 
    score_difference_average.

    
##Forms Included:
 - **SimpleMessage**
    - Used to send one line messages to the user (game created, game not found, 
    result of movement.
 - **NewGameForm**
    - Form to add users for a new game.
 - **OthelloGameForm**
    - Main representation of a game's state. Includes all relevant information
    (scores, players, game id, status), and the game board in json format.
 - **OthelloGameForms**
    - A Container for several OthelloGameForm to show a detailed list of 
    Othello games.
 - **OthelloGameHistoryForm**
    - Response form to show game moves for a given game id.
 - **OthelloHighScoreEntryForm**
    - Form to display game stats for one player including name, points, wins, and 
    winning streak.
 - **OthelloHighScoreForm**
    - Container for OthelloHighScoreEntryForm. It's used to build the list of top 
    scorers for the game.
 - **OthelloPlayerRankingFormEntry**
    - Form to display player rankings specific to the performance_index computed by 
    the datastore.
 - **OthelloPlayerRankingForm**
    - Container to build the list of top ranked players.

    - General purpose String container.
