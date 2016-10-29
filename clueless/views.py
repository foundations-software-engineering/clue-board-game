from django.http import HttpResponse
from django.template import loader

def index(request):
	#return HttpResponse("Welcome to the world of Clue-Less!")
	template = loader.get_template('clueless/index.html')
	context = {}
	return HttpResponse(template.render(context, request))
