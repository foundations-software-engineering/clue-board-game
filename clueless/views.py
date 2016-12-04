from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import Context, loader
from clueless.models import Accusation, Board, Card, Character, Game, Player, Room, SheetItem, STATUS_CHOICES, Suggestion, Weapon, WhoWhatWhere, Space
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# HttpResponse functions below here

def index(request):
	#return HttpResponse("Welcome to the world of Clue-Less!")
	template = loader.get_template('clueless/index.html')
	context = {}
	return HttpResponse(template.render(context, request))

def login(request):
	"""
	Logs in a user
	:param request:
	:return:
	"""

	#will be set to true if there is an issue logging in
	loginError = False

	if(request.method == "POST"):
		#get the username and password, and attempt to authenticate
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)
		#if the user authenticated, go to the next get param if set, otherwise go to homepage
		if user is not None:
			auth_login(request, user)
			redirectNext = request.GET.get('next')
			if redirectNext is not None:
				redirect(redirectNext)
			else:
				return redirect('index')
		else: #user didn't login right, give them a login error
			loginError = True

	#either the authentication failed, or they are coming to the login page for the first time.  Render the page
	template = loader.get_template('clueless/login.html')
	context = Context({'loginError':loginError})
	return HttpResponse(template.render(context, request))

def logout(request):
	"""
	Logs the user out
	:param request:
	:return:
	"""
	auth_logout(request)
	logger.info('did we get here?')
	return redirect('index')

@login_required
def lobby(request):
	"""
	This view produces a "lobby" displaying all not-started and active games
	to a particular user.  This view also gives the user the ability to start
	a new game
	:param request:
	:return:
	"""

	#get all player objects for user where games are not over
	currentPlayers = Player.objects.filter(
		user = request.user,
		currentGame__status__lt = 2)

	#concatenates all the player's game objects into a list
	currentGames = list()
	gameIdList = list()
	for p in currentPlayers:
		currentGames.append(p.currentGame)
		gameIdList.append(p.currentGame.id)

	#get all open, not started games that the current user could join
	openGames = Game.objects.filter(status__lt = 2).exclude(id__in = gameIdList)

	#create context and render template
	context = Context({'openGames':openGames, 'currentGames':currentGames})
	template = loader.get_template('clueless/lobby.html')
	return HttpResponse(template.render(context, request))

@login_required
def startgame(request):
	"""
	Provides the UI for intializing a game
	:param request:
	:return:
	"""
	template = loader.get_template('clueless/startgame.html')
	characterList = Character.objects.all().order_by('name')
	context = {'chracterList':characterList}
	return HttpResponse(template.render(context,request))

@login_required
def joingame(request, game_id):
	"""
	provides the UI for joining a game
	:param request:
	:param game_id: game_id of a game that hasn't been started that the user is in
	:return:
	"""
	template = loader.get_template('clueless/joingame.html')
	#get game object
	try:
		game = Game.objects.get(id = game_id)
	except Game.DoesNotExist:
		return redirect('index')
	#check whether user is already in game, if so, go to play game
	if game.isUserInGame(request.user):
		return redirect('playgame', game_id = game.id)
	#return a list of characters that haven't already been used in the game
	characterList = game.unusedCharacters()

	context = {'game':game, 'characterList': characterList}
	return HttpResponse(template.render(context, request))

@login_required
def begingame(request, game_id):
	"""
	Actually begins a game
	:param request:
	:param game_id: game_id of a game with more than 1 player, that hasn't started, that the user is the host of
	:return:
	"""
	template = loader.get_template('clueless/begingame.html')
	# get game object
	try:
		game = Game.objects.get(id=game_id)
	except Game.DoesNotExist:
		return redirect('index')

	#get a list of players currently in the game
	players = Player.objects.filter(currentGame__id = game_id)
	numOfPlayers = players.count()

	context = {'game': game, 'players': players, 'numOfPlayers': numOfPlayers}
	return HttpResponse(template.render(context, request))

@login_required
def playgame(request, game_id):
	"""
	UI for playing the game
	:param request:
	:param game_id: game_id of a game at status Started
	:return:
	"""

	try:
		game = Game.objects.get(id = game_id)
		player = Player.objects.get(user=request.user, currentGame=game)
	except Game.DoesNotExist:
		logger.error("Requested game_id doesn't exist")
		return HttpResponse(status=422, content="Requested game doesn't exist")
	except Player.DoesNotExist:
		logger.error("User does not have a player in this game")
		return HttpResponse(status=422, content="You are not a player in this game")

	if game.status == 0: #redirect to begingame lobby
		return redirect('begingame', game_id = game_id)

	spaces = Space.objects.all().order_by('posY', 'posX')
	context = {"game":game, "player":player, "spaces":spaces}
	template = loader.get_template('clueless/play.html')
	return HttpResponse(template.render(context,request))

@login_required
def playerturn(request):
	template = loader.get_template('clueless/playerturn.html')

	if request.method == 'POST':
		if 'user_id' or 'player_move' in request.POST:
			#store variables for easier usage
			user_id = request.user
			player_move = request.POST['player_move']
			new_position = request.POST['new_position']

			player = Player.objects.get(user = user_id)
			
			#redirect to correct page or perform logic check based on choice
			if player_move == "makeAccusation":
				template = loader.get_template('clueless/makeAccusation.html')
			elif player_move == "makeSuggestion":
				template = loader.get_template('clueless/makeSuggestion.html')
			elif player_move == "moveSpace":
				#TODO: logic for confirming space is valid 
				print("checking if player " + str(user_id) + " can move to " + new_position + " from " + str(player.currentSpace))
		else:
			#TODO: replace with logging later(don't want to replicate from grehg's but will use below commented out code)
			#logger.error('user_id or player_move not provided')
			print('user_id or player_move not provided')

	context = {}
	return HttpResponse(template.render(context,request))

@login_required
def detectivesheet(request, game_id, player_id):
	"""
	:param request:
	:param game_id: game_id of a game at status Started
	:param player_id: player_id of logged in player
	:return:
	"""
	try:
		game = Game.objects.get(id = game_id)
		player = Player.objects.get(id = player_id, currentGame = game)
	except Game.DoesNotExist:
		logger.error("Requested game_id doesn't exist")
		return HttpResponse(status=422, content="Requested game doesn't exist")
	except Player.DoesNotExist:
		logger.error("Requested player_id doesn't exist or is not part of this game")
		return HttpResponse(status=422, content="Requested player_id doesn't exist or is not part of this game")

	#check for permissions
	if request.user != player.user:
		logger.error('player_id does not match user')
		return HttpResponse(status = 403, content="logged in user does not match player_id")

	#get all of the sheet items for the player
	ds = player.getDetectiveSheet()

	template = loader.get_template('clueless/detectivesheet.html')
	context = {
		'characterSheetItems': ds.getCharacterSheetItems(),
		'roomSheetItems':ds.getRoomSheetItems(),
		'weaponSheetItems': ds.getWeaponSheetItems()
	}
	return HttpResponse(template.render(context, request))

@login_required
def gamestate(request):
	"""
	This view will do the following:

	:param request: POST request, with the following fields: game_id, player_id, cached_game_seq
	:return: If the gameState is the same as before, return {'changed':false}.Otherwise, render a JSON representation of the current game state
	"""
	#parse request
	if request.method != 'POST':
		logger.error('request is not a post request')
		return HttpResponse(status=417, content="must be POST request")
	#check for valid request parameters
	elif 'game_id' not in request.POST:
		logger.error('game_id not provided')
		return HttpResponse(status = 417, content="game_id not provided")
	elif 'player_id' not in request.POST:
		logger.error('player_id not provided')
		return HttpResponse(status = 417, content="player_id not provided")
	elif 'cached_game_seq' not in request.POST:
		logger.error('cached_game_seq not provided')
		return HttpResponse(status = 417, content="cached_game_seq not provided")

	game_id = request.POST.get('game_id')
	player_id = request.POST.get('player_id')
	cached_game_seq = int(request.POST.get('cached_game_seq'))
	#get the object instances
	try:
		game = Game.objects.get(id = game_id)
		player = Player.objects.get(id = player_id)
	except Game.DoesNotExist:
		logger.error('invalid game_id')
		return HttpResponse(status = 422, content="invalid game_id")
	except Player.DoesNotExist:
		logger.error('invalid player_id')
		return HttpResponse(status = 422, content='invalid player_id')

	#user must be the same as the player, and must be in the game
	if request.user != player.user:
		logger.error('player_id does not match user')
		return HttpResponse(status = 403, content="logged in user does not match player_id")
	elif player.currentGame != game:
		logger.error('player is not in requested game')
		return HttpResponse(status=403, content="player is not in requested game")

	responseData = {}
	#now, we can actually begin the view logic
	if cached_game_seq == game.currentSequence:
		#game has not been updated
		responseData['changed'] = False
	else:
		responseData['changed'] = True
		responseData['gamestate'] = game.gameStateJSON(player)

	return JsonResponse(responseData)


# Controller functions will go below here
@login_required
def start_game_controller(request):
	"""
	Creates a game with the given host defined by his/her user_id. Also provided
	is the host's designated character. Other players may join later, as this
	game is not available in the lobby as a joinable game.
	:param request: POST request with character_id and game_name
	:return:
	"""
	if request.method == 'POST':
		#validate required fields are present
		if 'character_id' not in request.POST:
			logger.error('character_id not provided')
			return redirect('startgame')
		elif 'game_name' not in request.POST:
			logger.error('game name not provided')
			return redirect('startgame')
		else:
			#can get logged in user direct from request object
			user = request.user
			character_id = request.POST.get('character_id')
			game_name = request.POST.get('game_name')

			#get character object
			try:
				character = Character.objects.get(card_id = character_id)
			except ObjectDoesNotExist: # Possible User.DoesNotExist
				logger.error('''character not found (Did you forget to add the
				character in the admin panel?''')
				return redirect('startgame')

			# Constructs our game, saves the changes and starts it
			game = Game(name = game_name)

			# Create a Player object for the Host
			player = Player(user = user, character = character, currentSpace = character.defaultSpace)
			player.save()

			#initialize the game, save, add player, and redirect
			game.initializeGame(player)
			game.save()

			game.addPlayer(player)
			game.save()

			# kewl, we are done now.  Let's send our user to the game interface
			return redirect('begingame', game_id = game.id)
	else:
		logger.error('POST expected, actual ' + request.method)

@login_required
def join_game_controller(request):
	"""
	Adds a player to a game
	Request should include a game_id and a character_id
	:param request: POST request with character_id and game_id
	:return:
	"""
	if request.method == 'POST':
		#validate necessary fields are present
		if 'character_id' not in request.POST:
			logger.error('character_id not provided')
			return redirect('joingame')
		elif 'game_id' not in request.POST:
			logger.error('game_id not provided')
			return redirect('joingame')
		else:
			#can get logged in user direct from request object
			user = request.user
			#get ids from post
			character_id = request.POST.get('character_id')
			game_id = request.POST.get('game_id')
			#get object instances
			try:
				character = Character.objects.get(card_id = character_id)
			except Character.DoesNotExist:
				logger.error('''Character not found''')
				return redirect('joingame')

			try:
				game = Game.objects.get(id = game_id)
			except Game.DoesNotExist:
				logger.error('''Game not found''')
				return redirect('joingame')

			#creates a player object for the new user
			player = Player(user=user, character=character, currentSpace=character.defaultSpace)
			player.save()

			# adds user/player to game
			if game.status != 0:
				logger.error('''Game already started''')
				#if user is in game, go to game, otherwise go to lobby
				if game.isUserInGame(user):
					return redirect('playgame', game_id=game.id)
				else:
					return redirect('lobby')
			elif game.isUserInGame(user):
				logger.error('''User already in game''')
				return redirect('begingame', game_id=game.id)
			else:
				game.addPlayer(player)

			game.save()

			# kewl, we are done now.  Let's send our user to the game interface
			return redirect('begingame', game_id = game.id)
	else:
		logger.error('POST expected, actual ' + request.method)

@login_required
def begin_game_controller(request):
	"""
	Begins a game
	:param request: POST with game_id
	:return:
	"""
	if request.method == 'POST':
		if 'game_id' not in request.POST:
			logger.error('game_id not provided')
			return redirect('begingame')
		else:
			#can get logged in user direct from request object
			user = request.user
			#get ids from post and attempt to lookup model objects
			game_id = request.POST.get('game_id')

			try:
				game = Game.objects.get(id = game_id)
			except Game.DoesNotExist:
				logger.error('''Game not found''')
				return redirect('begingame')

			#check conditions, start game if conditions met
			game.startGame(request.user)
			game.save()

			# kewl, we are done now.  Let's send our user to the game interface
			return redirect('playgame', game_id = game.id)
	else:
		logger.error('POST expected, actual ' + request.method)

def make_suggestion(request):
	"""
	Creates a suggestion that is composed of a character, weapon and room
	"""
	if request.method == 'POST':
		if 'character' or 'weapon' or 'room' not in request.POST:
			logger.error('character or weapon or room not provided')
			# TODO Redirect to appropriate error page
		else:
			# Gets our expected id fields from the user's POST
			character_name = request.POST('character_name')
			weapon_id = request.POST('weapon_id')
			room_id = request.POST('room_id')

			try:
				character = User.objects.get(character = character_name)
			except ObjectDoesNotExist: # Possible User.DoesNotExist
				logger.error('''character not found (Did you forget to add the
				character in the admin panel?''')
				# TODO Redirect to appropriate error page

			try:
				weapon = User.objects.get(weapon = weapon_id)
			except ObjectDoesNotExist: # Possible User.DoesNotExist
				logger.error('''weapon not found (Did you forget to add the
				weapon in the admin panel?''')
				# TODO Redirect to appropriate error page

			try:
				room = User.objects.get(room = room_id)
			except ObjectDoesNotExist: # Possible User.DoesNotExist
				logger.error('''room not found (Did you forget to add the
				room in the admin panel?''')
				# TODO Redirect to appropriate error page

			whoWhatWhere = WhoWhatWhere()
			whoWhatWhere.character = character
			whoWhatWhere.weapon = weapon
			whoWhatWhere.room = room

			suggestion = Suggestion()
			suggestion.whoWhatWhere = whoWhatWhere
	else:
		logger.error('POST expected, actual ' + request.method)

def make_accusation(request):
	"""
	Creates a accusation that is composed of a character, weapon and room.
	"""
	if request.method == 'POST':
		if 'character' or 'weapon' or 'room' not in request.POST:
			logger.error('character or weapon or room not provided')
			# TODO Redirect to appropriate error page
		else:
			# Gets our expected id fields from the user's POST
			character_name = request.POST('character_name')
			weapon_id = request.POST('weapon_id')
			room_id = request.POST('room_id')

			try:
				character = User.objects.get(character = character_name)
			except ObjectDoesNotExist: # Possible User.DoesNotExist
				logger.error('''character not found (Did you forget to add the
				character in the admin panel?''')
				# TODO Redirect to appropriate error page

			try:
				weapon = User.objects.get(weapon = weapon_id)
			except ObjectDoesNotExist: # Possible User.DoesNotExist
				logger.error('''weapon not found (Did you forget to add the
				weapon in the admin panel?''')
				# TODO Redirect to appropriate error page

			try:
				room = User.objects.get(room = room_id)
			except ObjectDoesNotExist: # Possible User.DoesNotExist
				logger.error('''room not found (Did you forget to add the
				room in the admin panel?''')
				# TODO Redirect to appropriate error page

			whoWhatWhere = WhoWhatWhere()
			whoWhatWhere.character = character
			whoWhatWhere.weapon = weapon
			whoWhatWhere.room = room

			accusation = Accusation()
			accusation.whoWhatWhere = whoWhatWhere
	else:
		logger.error('POST expected, actual ' + request.method)

def manualsheetitemcheck(request, game_id, player_id):
	"""
	This view manually checks off a sheet item for a given player
	:param request: POST, includes int field "check" and "card_id"
	:param game_id:
	:param player_id:
	:return:
	"""
	# parse request
	if request.method != 'POST':
		logger.error('request is not a post request')
		return HttpResponse(status=417, content="must be POST request")
	# check for valid request parameters
	elif 'card_id' not in request.POST:
		logger.error('card_id not provided')
		return HttpResponse(status=417, content="card_id not provided")
	elif 'check' not in request.POST:
		logger.error('check not provided')
		return HttpResponse(status=417, content="check not provided")

	card_id = request.POST.get("card_id")

	# get the object instances
	try:
		game = Game.objects.get(id=game_id)
		player = Player.objects.get(id=player_id)
		card = Card.objects.get(card_id = card_id)
	except Game.DoesNotExist:
		logger.error('invalid game_id')
		return HttpResponse(status=422, content="invalid game_id")
	except Player.DoesNotExist:
		logger.error('invalid player_id')
		return HttpResponse(status=422, content='invalid player_id')
	except Card.DoesNotExist:
		logger.error('invalid card')
		return HttpResponse(status=422, content='invalid card')

	# user must be the same as the player, must be in the game, and sheet item must belong to player
	if request.user != player.user:
		logger.error('player_id does not match user')
		return HttpResponse(status=403, content="logged in user does not match player_id")
	elif player.currentGame != game:
		logger.error('player is not in requested game')
		return HttpResponse(status=403, content="player is not in requested game")

	check = int(request.POST.get("check"))
	player.getDetectiveSheet().makeNote(card, check > 0, manuallyChecked = True)

	return HttpResponse(status = 200)
