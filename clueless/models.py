from django.db import models

class Room(models.Model):
	title = models.CharField(max_length=30)
	background = models.CharField(max_length=50)
	position = models.IntegerField()

	def getTitle(self):
		return self.title

	def getPosition(self):
		return self.position

