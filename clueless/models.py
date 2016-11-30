from django.db import models
from django.contrib.auth.models import User

import datetime

"""
Implementation of status enum as a Django IntergerField of choices
"""
NOT_STARTED = 0
STARTED = 1
COMPLETE = 2
STATUS_CHOICES = (
    (NOT_STARTED, 'Not Started'),
    (STARTED, 'Started'),
    (COMPLETE, 'Complete'),
)

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
    spaceNorth = models.OneToOneField('self', related_name='spaceSouth', blank=True, null=True)
    spaceWest = models.OneToOneField('self', related_name='spaceEast', blank=True, null=True)
    spaceCollector = models.ForeignKey(SpaceCollection)

    def __str__(self):
        return("({},{})".format(self.posX, self.posY))

class Player(models.Model):
    """
    Represents a player in the context of a clueless game.  Ties back to Django user
    """
    user = models.ForeignKey(User)
    currentSpace = models.ForeignKey(Space)
    currentGame = models.ForeignKey('Game', blank=True, null=True) # game not defined yet, using string as lazy lookup
    character = models.ForeignKey('Character', blank=True)

    def __str__(self):
        return("user: {}, currentSpace: {}, currentGame: {}, character: {}".format(
            self.user.__str__(), self.currentSpace.__str__(), self.currentGame.__str__(), self.character.__str__()
        ))

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

    def compare(self, otherCard):
        """
        Compares two Card objects
        :param otherCard: object of class Card
        :return: true if objects are equal, false otherwise
        """
        return(self.name == otherCard.name)

    def __str__(self):
        return(self.name)


class Room(SpaceCollection, Card):
    """
    Represents each room.
	"""
    pass


class Character(Card):
    """
    Represents each character in the game clue (the actual character, like Mr. Green)
	"""
    defaultSpace = models.ForeignKey(Space)

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

    def compare(self, otherWhoWhatWhere):
        """
        :param otherWhoWhatWhere: object of class WhoWhatWhere
        :return: true if room, character and weapon are all equal
        """
        roomEqual = self.room.compare(otherWhoWhatWhere.room)
        charEqual = self.character.compare(otherWhoWhatWhere.character)
        weaponEqual = self.weapon.compare(otherWhoWhatWhere.weapon)
        return(roomEqual and charEqual and weaponEqual)

    def __str__(self):
        return("character: {}, room: {}, weapon: {}".format(
            self.character.__str__(), self.room.__str__(), self.weapon.__str__()
        ))

class Turn(models.Model):
    """
    References the player, and contains a list of sequential actions performed by the player during one turn
    """
    player = models.ForeignKey(Player)
    game = models.ForeignKey('Game') #Game class not defined yet, referencing by string
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def getAvailableActions(self):
        """
        :return: Set of Action subclass class objects that can be taken at this point
        """
        #TODO: Implement this method
        return(None)

    def takeAction(self, action):
        """
        Performs an action
        :param action: Subclass of Action, which will have its performAction function called
        :return:
        """
        #TODO: implement this method
        return(None)

    def endTurn(self):
        """
        Ends this turn
        """
        pass

class Action(models.Model):
    """
    Any player action a player can take during a turn
    """
    turn = models.ForeignKey(Turn, blank=True)
    description = models.CharField(max_length=255, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def validate(self):
        """
        :return: boolean Can the action be validly taken
        """
        raise NotImplementedError("Subclasses of Action need to implement abstract method validate")

    def performAction(self):
        """
        Performs the action
        """
        raise NotImplementedError("Subclasses of Action need to implement abstract method performAction")


class Suggestion(Action):
    """
    A suggestion action taken by the player
    """
    whoWhatWhere = models.ForeignKey(WhoWhatWhere)

class Accusation(Action):
    """
    An accusation action taken by the player.  Either the player wins the game or they lose!
    """
    whoWhatWhere = models.ForeignKey(WhoWhatWhere)

class Move(Action):
    """
    Any move a player makes
    """
    fromSpace = models.ForeignKey(Space, related_name='fromSpace')
    toSpace = models.ForeignKey(Space, related_name='toSpace')

class CaseFile(WhoWhatWhere):
    """
    Class to be used for the secret CaseFile for a Game
    """
    @classmethod
    def createRandom(cls):
        """
        Static class method, to be used instead of constructor in most cases
        :return: CaseFile with random selections for room, character and weapon
        """
        #TODO: actually write this function...
        randCaseFile = CaseFile()
        randCaseFile.character = Character.objects.all()[0]
        randCaseFile.room = Room.objects.all()[0]
        randCaseFile.weapon = Weapon.objects.all()[0]
        return(randCaseFile)

class Game(models.Model):
    """
    Parent game object
    """
    caseFile = models.ForeignKey(CaseFile)
    board = models.ForeignKey(Board)
    status = models.IntegerField(choices = STATUS_CHOICES, default = 1)
    startTime = models.DateTimeField(default = datetime.datetime.now, blank = True)
    lastUpdateTime = models.DateTimeField(default=datetime.datetime.now, blank=True)
    hostPlayer = models.ForeignKey(Player)

    def initializeGame(self, playerHost):
        """
        Sets up a game with all the defaults
        :param playerHost: A player object representing the player that started the game
        :return:
        """
        self.hostPlayer = playerHost
        self.board = Board.objects.all()[0]
        self.status = NOT_STARTED
        randCaseFile = CaseFile.createRandom()
        randCaseFile.save()
        self.caseFile = randCaseFile

    def unusedCharacters(self):
        """
        Gets a query set of character objects that have not been taken by a player yet
        :return:
        """
        #TODO: actually implement this method...
        return Character.objects.all()

    def startGame(self):
        """
        Starts a game
        :param playerHost: player that will be the host
        """
        #TODO: implement this method
        pass

    def canUserJoinGame(self, user):
        """
        Checks whether a user can join the game or not
        :param user:
        :return: True if user can join game
        """
        try:
            player = Player.objects.get(currentGame__id=self.id, user__id=user.id)
        except:
            return True
        return False

    def addPlayer(self, player):
        """
        Adds a player to the game
        :param player: Player to be added
        """
        if self.canUserJoinGame(player.user):
            player.currentGame = self
            player.save()
        else:
            raise PermissionError("User is already a player in this game")

    def endGame(self, winningPlayer):
        """
        Ends the game
        :param winningPlayer: Player who won
        """
        #TODO: implement this method
        pass

    def loseGame(self, losingPlayer):
        """
        Ends the game for a losing player
        :param losingPlayer: Player who lost (bad accusation
        """
        #TODO: implement this method
        pass

class DetectiveSheet(models.Model):
    """
    Detective Sheet a player fills out.  As card are discovered, a player checks off different cards as no longer
    possible
    """
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)

    def getRoomsLeft(self):
        """
        :return: Set of Room object that a player has not yet checked off
        """
        #TODO: implement this method
        return(None)

    def getCharactersLeft(self):
        """
        :return: Set of Character objects that a player has not yet checked off
        """
        # TODO: implement this method
        return (None)

    def getWeaponsLeft(self):
        """
        :return: Set of Weapon objects that a player has not yet checked off
        """
        # TODO: implement this method
        return (None)

    def makeNote(self, card, checked):
        """
        Notes whether a player has checked off a particular card or not
        :param card: Card that is being checked off
        :param checked: boolean whether to check or uncheck
        """
        #TODO: implement this method
        pass

class SheetItem(models.Model):
    """
    A sheet item is an item on a DectiveSheet, and represents whether a user has checked off a specific card yet
    """
    detectiveSheet = models.ForeignKey(DetectiveSheet)
    card = models.ForeignKey(Card)
    checked = models.BooleanField
