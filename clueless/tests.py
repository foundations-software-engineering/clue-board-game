from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from clueless.models import Character, Game, Player


class GameModelTests(TestCase):

    @classmethod
    def setUpClass(cls):
        # create all default objects in the test database
        call_command('create_default_objects')
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
