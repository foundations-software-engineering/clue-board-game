from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    """
    Board object for the entire game.  Should be referenced by multiple games and space collections
    """
    pass

class SpaceCollection(models.Model):
    """
    Any implementations should occupy a set of spaces on the board
    """
    board = models.ForeignKey(Board)

class Space(models.Model):
    """
    Represents a space on the game board, with an X Y position and all neighbor spaces
    """
    posX = models.IntegerField()
    posY = models.IntegerField()
    spaceNorth = models.OneToOneField('self', related_name='spaceSouth', blank=True)
    spaceEast = models.OneToOneField('self', related_name='spaceWest', blank=True)
    spaceCollector = models.ForeignKey(SpaceCollection)

class Player(models.Model):
    """
    Represents a player in the context of a clueless game.  Ties back to Django user
    """
    user = models.ForeignKey(User)
    currentSpace = models.ForeignKey(Space)
    currentGame = models.ForeignKey('Game') # game not defined yet, using string as lazy lookup

class Hallway(SpaceCollection):
    """
    Hallway in the game
    """
    pass

class SecretPassage(SpaceCollection):
    """
    Secret Passage in the game
    """
    pass

class Card(models.Model):
    """
    A game Card.  Can either be a Room, Character, or Weapon
    """
    card_id = models.AutoField(primary_key=True) #had to override, due to multiple inheritence conflicts later
    name = models.CharField(max_length=30)

    def __eq__(self, otherCard):
        """
        Compares two Card objects
        :param otherCard: object of class Card
        :return: true if objects are equal, false otherwise
        """
        return self.name == otherCard.name


class Room(SpaceCollection, Card):
    """
    Represents each room.
	"""
    background = models.CharField(max_length=50)
    position = models.IntegerField()

    # :( not very pythonic.  Commenting out
    """
	def getTitle(self):
		return self.title

	def getPosition(self):
		return self.position
	"""


class Character(Card):
    """
    Represents each character in the game clue (the actual character, like Mr. Green)
	"""
    pass

class Weapon(Card):
    """
    Represents each weapon
	"""
    pass

class WhoWhatWhere(models.Model):
    """
    Class containing references to a Room, Weapon and Character.  A single instance of WhoWhereWhat is created at the
	start of the game as the confidential case file.  An instance of WhoWhereWhat is created every time an accusation or
	suggestion is made.
	"""
    character = models.ForeignKey(Character)
    weapon = models.ForeignKey(Weapon)
    room = models.ForeignKey(Room)

    def __eq__(self, otherWhoWhatWhere):
        """
        :param otherWhoWhatWhere: object of class WhoWhatWhere
        :return: true if room, character and weapon are all equal
        """
        roomEqual = self.room.__eq__(otherWhoWhatWhere.room)
        charEqual = self.character.__eq__(otherWhoWhatWhere.character)
        weaponEqual = self.weapon.__eq__(otherWhoWhatWhere.weapon)
        return(roomEqual and charEqual and weaponEqual)

class Turn(models.Model):
    """
    References the player, and contains a list of sequential actions performed by the player during one turn
    """
    player = models.ForeignKey(Player)
    game = models.ForeignKey('Game') #Game class not defined yet, referencing by string

class Action(models.Model):
    """
    Any player action a player can take during a turn
    """
    turn = models.ForeignKey(Turn)

class Suggestion(Action):
    """
    A suggestion action taken by the player
    """
    pass

class Accusation(Action):
    """
    An accusation action taken by the player.  Either the player wins the game or they lose!
    """
    pass

class Move(Action):
    """
    Any move a player makes
    """
    pass

class Game(models.Model):
    """
    Parent game object
    """
    caseFile = models.ForeignKey(WhoWhatWhere)
    board = models.ForeignKey(Board)

class DetectiveSheet(models.Model):
    """
    Detective Sheet a player fills out.  As card are discovered, a player checks off different cards as no longer
    possible
    """
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)

class SheetItem(models.Model):
    """
    A sheet item is an item on a DectiveSheet, and represents whether a user has checked off a specific card yet
    """
    detectiveSheet = models.ForeignKey(DetectiveSheet)
    card = models.ForeignKey(Card)
    checked = models.BooleanField