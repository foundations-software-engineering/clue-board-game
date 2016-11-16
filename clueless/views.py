from django.http import HttpResponse
from django.template import loader

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

# Controller functions will go below here
