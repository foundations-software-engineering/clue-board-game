from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import loader
from clueless.models import Game, Player
from django.shortcuts import redirect

def index(request):
	# return HttpResponse("Welcome to the world of Clue-Less!")
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
	# get the user_id of the user requesting to start a game
	user_id = request.POST['user_id']

	# get the character_id of the user requesting to start a game
	character_name = request.POST['character_name']

	# retrieve the User object by looking it up by Id.  This will retrieve the saved instance of User from the database
	current_user = User.objects.get(id=user_id)

	# create a new player object for that user
	host_player = Player(user=current_user)

	# now we are going to start the game!!!
	new_game = Game()
	new_game.startGame(host_player)

	# alright, we have started the game.  Let's save our objects to the database!
	host_player.save()
	new_game.save()

	# kewl, we are done now.  Let's send our user to the game interface
	return redirect('view_game', gameid=new_game.id)
