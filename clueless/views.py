from django.http import HttpResponse
from django.template import loader
from .models import *
from clueless import models

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
