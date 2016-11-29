from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import Context, loader
from clueless.models import Accusation, Board, Character, Game, Player, Room, STATUS_CHOICES, Suggestion, Weapon, WhoWhatWhere
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
	openGames = Game.objects.filter(status = 0).exclude(id__in = gameIdList)

	#create context and render template
	context = Context({'openGames':openGames, 'currentGames':currentGames})
	template = loader.get_template('clueless/lobby.html')
	return HttpResponse(template.render(context, request))

@login_required
def startgame(request):
	#return HttpResponse("Welcome to the game")
	template = loader.get_template('clueless/startgame.html')
	characterList = Character.objects.all().order_by('name')
	context = {'chracterList':characterList}
	return HttpResponse(template.render(context,request))

@login_required
def playgame(request, game_id):
	#return HttpResponse("Welcome to the game")
	template = loader.get_template('clueless/play.html')
	game = Game.objects.get(id = game_id)
	context = {"game":game}
	return HttpResponse(template.render(context,request))

@login_required
def playerturn(request):
	template = loader.get_template('clueless/playerturn.html')
	context = {}

	if request.method == 'POST':
		if 'user_id' or 'player_move' in request.POST:
			#store variables for easier usage
			user_id = request.POST['user_id']
			player_move = request.POST['player_move']
			new_position = request.POST['new_position']

			#TODO: mocking the player for now, but will use database later to get Player once we're actually population it
			#player = Player.objects.get(user = user_id)
			player = Player()
			player.currentPostion = "library"
			
			#redirect to correct page or perform logic check based on choice
			if player_move == "makeAccusation":
				#TODO: actually redirect to accusation page, below code should work once that stuff is merged in
				#template = loader.get_template('clueless/makeAccusation.html')
				print("redirect to makeAccusation page")
			elif player_move == "makeSuggestion":
				#TODO: actually redirect to suggestion page, below code should work once that stuff is merged in
				#template = loader.get_template('clueless/makeSuggestion.html')
				print("redirect to makeSuggestion page")
			elif player_move == "moveSpace":
				#TODO: logic for confirming space is valid 
				print("checking if player " + user_id + " can move to " + new_position + " from " + player.currentPostion)
		else:
			#TODO: replace with logging later(don't want to replicate from grehg's but will use below commented out code)
			#logger.error('user_id or player_move not provided')
			print('user_id or player_move not provided')


	return HttpResponse(template.render(context,request))

# Controller functions will go below here
@login_required
def start_game_controller(request):
	"""
	Creates a game with the given host defined by his/her user_id. Also provided
	is the host's designated character. Other players may join later, as this
	game is not available in the lobby as a joinable game.
	"""
	if request.method == 'POST':
		if 'character_id' not in request.POST:
			logger.error('character_id not provided')
			return redirect('startgame')
		else:
			#can get logged in user direct from request object
			user = request.user
			character_id = request.POST.get('character_id')

			try:
				character = Character.objects.get(card_id = character_id)
			except ObjectDoesNotExist: # Possible User.DoesNotExist
				logger.error('''character not found (Did you forget to add the
				character in the admin panel?''')
				return redirect('startgame')

			# Constructs our game, saves the changes and starts it
			game = Game()

			# Create a Player object for the Host
			player = Player()
			player.user = user
			player.character = character
			player.currentSpace = character.defaultSpace
			player.save()

			game.initializeGame(player)
			game.save()

			# kewl, we are done now.  Let's send our user to the game interface
			return redirect('playgame', game_id = game.id)
	else:
		logger.error('POST expected, actual ' + request.method)


def make_suggestion(request):
	"""
	Creates a suggestion (note: same as make_accusation, perhaps factor this commonality out)
	"""

	if request.method == 'POST':
		if 'character' or 'weapon' or 'room' not in request.POST:
			logger.error('character or weapon or room not provided')
		else:
			# Gets our expected id fields from the user's POST
			character_id = request.POST('character')
			weapon_id = request.POST('weapon')
			room_id = request.POST('room')

			# Lookup the IDs in our database
			character = Character.objects.get(id = character_id)
			weapon = Weapon.objects.get(id = weapon_id)
			room = Room.objects.get(id = room_id)

			# Creates our WhoWhatWhere object
			whoWhatWhere = WhoWhatWhere()
			whoWhatWhere.character = character
			whoWhatWhere.weapon = weapon
			whoWhatWhere.room = room




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

def make_accusation(request):
	"""
	Creates a accusation (note: same as make_suggestion, perhaps factor this commonality out)
	"""
	if request.method == 'POST':
		if 'character' or 'weapon' or 'room' not in request.POST:
			logger.error('character or weapon or room not provided')
		else:
			# Gets our expected fields from the user's POST
			character_id = request.POST('character')
			weapon_id = request.POST('weapon')
			room_id = request.POST('room')

			# Lookup the IDs in our database
			character = Character.objects.get(id = character_id)
			weapon = Weapon.objects.get(id = weapon_id)
			room = Room.objects.get(id = room_id)

			# Creates our WhoWhatWhere object
			whoWhatWhere = WhoWhatWhere()
			whoWhatWhere.character = character
			whoWhatWhere.weapon = weapon
			whoWhatWhere.room = room
	else:
		logger.error('POST expected, actual ' + request.method)
