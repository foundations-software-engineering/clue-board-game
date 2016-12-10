from django.core.management.base import BaseCommand, CommandError
from clueless.models import Board, Character, Hallway, Room, SecretPassage, Space, Weapon

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    #def add_arguments(self, parser):
        #parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        print("Starting creation of default objects")
        defBoard = Board()
        defBoard.save()

        #create 6 default weapons
        Weapon(name = "Rope").save()
        Weapon(name = "Lead Pipe").save()
        Weapon(name = "Knife").save()
        Weapon(name = "Wrench").save()
        Weapon(name = "Candlestick").save()
        Weapon(name = "Revolver").save()

        #create 6 default rooms
        studyRoom = Room(name = "Study", board = defBoard)
        studyRoom.save()
        hallRoom = Room(name = "Hall", board = defBoard)
        hallRoom.save()
        loungeRoom = Room(name = "Lounge", board = defBoard)
        loungeRoom.save()
        libraryRoom = Room(name = "Library", board = defBoard)
        libraryRoom.save()
        billiardRoom = Room(name = "Billiard Room", board = defBoard)
        billiardRoom.save()
        diningRoom = Room(name = "Dining Room", board = defBoard)
        diningRoom.save()
        conservatoryRoom = Room(name = "Conservatory", board = defBoard)
        conservatoryRoom.save()
        ballRoom = Room(name = "Ballroom", board = defBoard)
        ballRoom .save()
        kitchenRoom = Room(name = "Kitchen", board = defBoard)
        kitchenRoom.save()

        #create hallways
        hallway01 = Hallway(name = "Study to Hall Hallway", board = defBoard)
        hallway01.save()
        hallway02 = Hallway(name= "Hall to Lounge Hallway", board = defBoard)
        hallway02.save()
        hallway03 = Hallway(name="Study to Library Hallway", board = defBoard)
        hallway03.save()
        hallway04 = Hallway(name="Hall to Billiards Hallway", board = defBoard)
        hallway04.save()
        hallway05 = Hallway(name = "Lounge to Dining Room Hallway", board = defBoard)
        hallway05.save()
        hallway06 = Hallway(name= "Library to Billiards Hallway", board = defBoard)
        hallway06.save()
        hallway07 = Hallway(name = "Billiards to Dining Room Hallway", board = defBoard)
        hallway07.save()
        hallway08 = Hallway(name = "Library to Conservatory Hallway", board = defBoard)
        hallway08.save()
        hallway09 = Hallway(name = "Billiards to Ballroom Hallway", board = defBoard)
        hallway09.save()
        hallway10 = Hallway(name= "Dining Room to Kitchen Hallway", board = defBoard)
        hallway10.save()
        hallway11 = Hallway(name = "Conservatory to Ballroom Hallway", board = defBoard)
        hallway11.save()
        hallway12 = Hallway(name ="Ballroom to Kitchen Hallway", board = defBoard)
        hallway12.save()

        #create secretpassages
        psgStudy2Kitchen = SecretPassage()
        psgLounge2Conservatory = SecretPassage()

        #now, lets create the gameboard spaces
        #Create passageways
        s01_01 = Space(posX=1, posY=1, spaceCollector=studyRoom)
        s01_01.save()
        s02_01 = Space(posX=2, posY=1, spaceWest=s01_01, spaceCollector=hallway01)
        s02_01.save()
        s03_01 = Space(posX=3, posY=1, spaceWest=s02_01, spaceCollector=hallRoom)
        s03_01.save()
        s04_01 = Space(posX=4, posY=1, spaceWest=s03_01, spaceCollector=hallway02)
        s04_01.save()
        s05_01 = Space(posX=5, posY=1, spaceWest=s04_01,  spaceCollector=loungeRoom)
        s05_01.save()

        s01_02 = Space(posX=1, posY=2, spaceNorth=s01_01, spaceCollector=hallway03)
        s01_02.save()
        #passageways will be declared later
        s03_02 = Space(posX=3, posY=2, spaceNorth=s03_01, spaceCollector=hallway04)
        s03_02.save()
        # passageways will be declared later
        s05_02 = Space(posX=5, posY=2, spaceNorth=s05_01, spaceCollector=hallway05)
        s05_02.save()

        s01_03 = Space(posX=1, posY=3, spaceNorth=s01_02, spaceCollector=libraryRoom)
        s01_03.save()
        s02_03 = Space(posX=2, posY=3, spaceWest=s01_03, spaceCollector=hallway06)
        s02_03.save()
        s03_03 = Space(posX=3, posY=3, spaceNorth=s03_02, spaceWest=s02_03, spaceCollector=billiardRoom)
        s03_03.save()
        s04_03 = Space(posX=4, posY=3, spaceWest=s03_03, spaceCollector=hallway07)
        s04_03.save()
        s05_03 = Space(posX=5, posY=3, spaceNorth=s05_02, spaceWest=s04_03, spaceCollector=diningRoom)
        s05_03.save()

        s01_04 = Space(posX=1, posY=4, spaceNorth=s01_03, spaceCollector=hallway08)
        s01_04.save()
        # passageways will be declared later
        s03_04 = Space(posX=3, posY=4, spaceNorth=s03_03, spaceCollector=hallway09)
        s03_04.save()
        # passageways will be declared later
        s05_04 = Space(posX=5, posY=4, spaceNorth=s05_03, spaceCollector=hallway10)
        s05_04.save()

        s01_05 = Space(posX=1, posY=5, spaceNorth=s01_04, spaceSouth = s05_01, spaceCollector=conservatoryRoom)
        s01_05.save()
        s02_05 = Space(posX=2, posY=5, spaceWest=s01_05, spaceCollector=hallway11)
        s02_05.save()
        s03_05 = Space(posX=3, posY=5, spaceNorth=s03_04, spaceWest=s02_05, spaceCollector=ballRoom)
        s03_05.save()
        s04_05 = Space(posX=4, posY=5, spaceWest=s03_05, spaceCollector=hallway12)
        s04_05.save()
        s05_05 = Space(posX=5, posY=5, spaceNorth=s05_04, spaceWest=s04_05, spaceSouth = s01_01, spaceCollector=kitchenRoom)
        s05_05.save()

        #set up secret passage ways as spaces
        s01_01.spaceNorth = s05_05
        s01_01.save()
        s05_01.spaceNorth = s01_05
        s05_01.save()


        # create 6 default characters
        Character(name="Miss Scarlet", defaultSpace=s04_01, characterColor="Red").save()
        Character(name="Col. Mustard", defaultSpace=s05_02, characterColor="Yellow").save()
        Character(name="Mrs. White", defaultSpace=s04_05, characterColor="White").save()
        Character(name="Mr. Green", defaultSpace=s02_05, characterColor="Green").save()
        Character(name="Mrs. Peacock", defaultSpace=s01_04, characterColor="Blue").save()
        Character(name="Prof. Plum", defaultSpace=s01_02, characterColor="Purple").save()

        print("Finished!")
