from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from clueless.models import Character, Game, Player, Room, Weapon, WhoWhatWhere
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# HttpResponse functions below here

def index(request):
	#return HttpResponse("Welcome to the world of Clue-Less!")
	template = loader.get_template('clueless/index.html')
	context = {}
	return HttpResponse(template.render(context, request))


def startgame(request):
	#return HttpResponse("Welcome to the game")
	template = loader.get_template('clueless/startgame.html')
	context = {}
	return HttpResponse(template.render(context,request))

def playgame(request):
	#return HttpResponse("Welcome to the game")
	template = loader.get_template('clueless/play.html')
	context = {}
	return HttpResponse(template.render(context,request))

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
def start_game_controller(request):
	"""
	Creates a game with the given host defined by his/her user_id. Also provided
	is the host's designated character. Other players may join later, as this
	game is not available in the lobby as a joinable game.
	"""

	if request.method == 'POST':
		if'user_id' or 'character_name' not in request.POST:
			logger.error('user_id or character_name not provided')
			# TODO Redirect to appropriate error page
		else:
			# Gets our expected fields from the user's POST
			user_id = request.POST('user_id')
			character_name = request.POST('character_name')

			try:
				user = User.objects.get(id = user_id)
			except ObjectDoesNotExist: # Possible User.DoesNotExist
				logger.info('user not found, adding them now')
				# TODO create actual user object
				# TODO add user to database

			try:
				character = Character.objects.get(name = character_name)
			except ObjectDoesNotExist: # Possible User.DoesNotExist
				logger.error('''character not found (Did you forget to add the
				character in the admin panel?''')
				# TODO Redirect to appropriate error page

			# Create a Player object for the Host
			player = Player()
			player.user = user
			player.character = character

			# Constructs our game, saves the changes and starts it
			game = Game()
			game.addPlayer(player)
			game.save() # TODO: Check if this is to do be done before startGame()
			game.startGame()
	else:
		logger.error('POST expected, actual ' + request.method)

	# kewl, we are done now.  Let's send our user to the game interface
	return redirect('view_game', gameid=game.id)


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
