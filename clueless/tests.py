from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from clueless.models import Card, Character, Game, Player, Room, Weapon

class AAA_DBSetup(TestCase):
    """
    Sets up the database with default objects
    """
    @classmethod
    def setUpClass(cls):
        call_command('create_default_objects')

    @classmethod
    def tearDownClass(cls):
        pass

    def test_dummy(self):
        pass


class CardModelTests(TestCase):

    #begin tests
    def test_compare_works_when_both_cards(self):
        allCards = Card.objects.all()
        for i in range(0, allCards.count()-1):
            self.assertEqual(allCards[i].compare(allCards[i]), True)

        self.assertEqual(allCards[1].compare(allCards[4]), False)
        self.assertEqual(allCards[2].compare(allCards[3]), False)

    def test_compare_works_when_one_not_cards(self):
        character = Character.objects.all()[4]
        cCard = Card.objects.get(card_id = character.card_id)
        room = Room.objects.all()[3]
        rCard = Card.objects.get(card_id = room.card_id)
        weapon = Weapon.objects.all()[2]
        wCard = Card.objects.get(card_id = weapon.card_id)

        self.assertEqual(cCard.compare(character), True)
        self.assertEqual(character.compare(cCard), True)
        self.assertEqual(rCard.compare(room), True)
        self.assertEqual(room.compare(rCard), True)
        self.assertEqual(wCard.compare(weapon), True)
        self.assertEqual(weapon.compare(wCard), True)
        self.assertEqual(cCard.compare(weapon), False)
        self.assertEqual(room.compare(cCard), False)

    def test_compare_works_when_both_not_cards(self):
        character1 = Character.objects.all()[4]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[4]
        room1 = Room.objects.all()[3]
        room2 = Room.objects.all()[1]
        room3 = Room.objects.all()[3]
        weapon1 = Weapon.objects.all()[2]
        weapon2 = Weapon.objects.all()[5]
        weapon3 = Weapon.objects.all()[2]

        self.assertEqual(character1.compare(character3), True)
        self.assertEqual(character3.compare(character1), True)
        self.assertEqual(character2.compare(character3), False)
        self.assertEqual(character2.compare(room1), False)


        self.assertEqual(room1.compare(room3), True)
        self.assertEqual(room3.compare(room1), True)
        self.assertEqual(room2.compare(room3), False)
        self.assertEqual(room2.compare(weapon1), False)


        self.assertEqual(weapon1.compare(weapon3), True)
        self.assertEqual(weapon3.compare(weapon1), True)
        self.assertEqual(weapon2.compare(weapon3), False)
        self.assertEqual(weapon2.compare(character1), False)


class GameModelTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user1 = User.objects.create_user('testuser1', 'a@a.com', 'testuser1Password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('testuser2', 'a@a.com', 'testuser2Password')
        cls.user2.save()

        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()

    @classmethod
    def tearDownClass(cls):
        cls.player1.delete()
        cls.player2.delete()
        cls.user1.delete()
        cls.user2.delete()

    def setUp(self):
        self.g = Game(name = "test")

    def tearDown(self):
        self.g.delete()

    #begin tests

    def test_initializeGame(self):
        self.g.initializeGame(self.player1)
        self.g.save()

    def test_addPlayer_raises_error_when_player_in_game(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        with self.assertRaises(RuntimeError):
            self.g.addPlayer(self.player1)

    def test_addPlayer_raises_error_when_user_in_game_with_different_player(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        newCharacter = Character.objects.all()[2]
        newPlayer = Player(user=self.user1, character=newCharacter, currentSpace=newCharacter.defaultSpace)
        with self.assertRaises(RuntimeError):
            self.g.addPlayer(newPlayer)

    def test_addPlayer_raises_error_when_character_in_game(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        newCharacter = Character.objects.all()[0]
        newPlayer = Player(user=self.user2, character=newCharacter, currentSpace=newCharacter.defaultSpace)
        with self.assertRaises(RuntimeError):
            self.g.addPlayer(newPlayer)

    def test_beginGame_raise_error_with_no_players(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        with self.assertRaises(RuntimeError):
            self.g.startGame(self.player1)

    def test_beginGame_raise_error_with_one_player(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        with self.assertRaises(RuntimeError):
            self.g.startGame(self.player1)

    def test_beginGame_raise_error_with_wrong_host(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        with self.assertRaises(RuntimeError):
            self.g.startGame(self.player2)

    def test_beginGame_raise_error_when_already_started(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.status = 1
        with self.assertRaises(RuntimeError):
            self.g.startGame(self.player1)

    def test_beginGame_works_with_2_players(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.save()

    def test_unusedCharacters_returns_all_when_no_players(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.assertEqual(self.g.unusedCharacters().count(), 6)

    def test_unusedCharacters_correct_when_1_player(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.assertEqual(self.g.unusedCharacters().count(), 5)
        self.assertNotIn(self.player1.character, self.g.unusedCharacters())

    def test_unusedCharacters_correct_when_1_player(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.assertEqual(self.g.unusedCharacters().count(), 4)
        self.assertNotIn(self.player1.character, self.g.unusedCharacters())
        self.assertNotIn(self.player2.character, self.g.unusedCharacters())

    def test_isUserInGame_false_when_no_players(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.assertEqual(self.g.isUserInGame(self.user1), False)
        self.assertEqual(self.g.isUserInGame(self.user2), False)

    def test_isUserInGame_correct_when_1_player(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.assertEqual(self.g.isUserInGame(self.user1), True)
        self.assertEqual(self.g.isUserInGame(self.user2), False)

    def test_isUserInGame_correct_when_2_player(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.assertEqual(self.g.isUserInGame(self.user1), True)
        self.assertEqual(self.g.isUserInGame(self.user2), True)

    def test_isCharacterInGame_false_when_no_players(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.assertEqual(self.g.isCharacterInGame(self.player1.character), False)
        self.assertEqual(self.g.isCharacterInGame(self.player2.character), False)
        self.assertEqual(self.g.isCharacterInGame(Character.objects.all()[3]), False)

    def test_isCharacterInGame_correct_when_1_player(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.assertEqual(self.g.isCharacterInGame(self.player1.character), True)
        self.assertEqual(self.g.isCharacterInGame(self.player2.character), False)
        self.assertEqual(self.g.isCharacterInGame(Character.objects.all()[3]), False)

    def test_isCharacterInGame_correct_when_2_player(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.assertEqual(self.g.isCharacterInGame(self.player1.character), True)
        self.assertEqual(self.g.isCharacterInGame(self.player2.character), True)
        self.assertEqual(self.g.isCharacterInGame(Character.objects.all()[3]), False)
