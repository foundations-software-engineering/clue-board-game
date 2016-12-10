from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
import json

from clueless.models import Accusation, Card, CardReveal, CaseFile, Character, DetectiveSheet, Game, Move, Player, Room, SheetItem, Space, Suggestion, Weapon, WhoWhatWhere


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


class CardRevealModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        # build users
        cls.user1 = User.objects.create_user('gamestatetestuser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('gamestatetestuser2', 'a@a.com', 'password')
        cls.user2.save()
        cls.user3 = User.objects.create_user('gamestatetestuser3', 'a@a.com', 'password')
        cls.user3.save()

        # build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[2]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()
        cls.player3 = Player(user=cls.user3, character=character3, currentSpace=character3.defaultSpace)
        cls.player3.save()

        cls.player1.currentSpace = Space.objects.get(posX=5, posY=1)

        cls.game1 = Game()
        cls.game1.initializeGame(cls.player1)
        cls.game1.save()
        cls.game1.addPlayer(cls.player1)
        cls.game1.addPlayer(cls.player2)
        cls.game1.addPlayer(cls.player3)
        cls.game1.startGame(cls.user1)

        cls.game1.refresh_from_db()
        cls.player2.refresh_from_db()

        turn = cls.game1.currentTurn
        cls.characterCard = cls.player2.getDetectiveSheet().getCharacterSheetItems().filter(initiallyDealt = True)[0].card
        cls.character = Character.objects.get(card_id = cls.characterCard.card_id)
        room = Room.objects.get(id=cls.player1.currentSpace.spaceCollector.id)
        weapon = Weapon.objects.all()[0]

        cls.p1Suggestion = Suggestion.createSuggestion(turn, cls.character, room, weapon)

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.player3.delete()
        cls.game1.delete()

    def test_createCardReveal_returns_saved_CardReveal(self):
        cr = CardReveal.createCardReveal(self.p1Suggestion)
        self.assertIsNotNone(cr.id)

    def test_createCardReveal_has_right_player(self):
        cr = CardReveal.createCardReveal(self.p1Suggestion)
        self.assertEquals(cr.revealingPlayer, self.player2)

    def test_hasNext_returns_true_when_has_next(self):
        cr = CardReveal.createCardReveal(self.p1Suggestion)
        self.assertEquals(cr.hasNext(), True)

    def test_hasNext_returns_false_when_not_has_next(self):
        cr = CardReveal.createCardReveal(self.p1Suggestion)
        cr1 = cr.createNext()
        self.assertEquals(cr1.hasNext(), False)

    def test_createNext_returns_saved_Card_Reveal(self):
        cr = CardReveal.createCardReveal(self.p1Suggestion)
        cr1 = cr.createNext()
        self.assertIsNotNone(cr1.id)

    def test_createNext_has_right_player(self):
        cr = CardReveal.createCardReveal(self.p1Suggestion)
        cr1 = cr.createNext()
        self.assertEquals(cr1.revealingPlayer, self.player3)

    def test_createNext_raises_Runtime_when_no_next(self):
        cr = CardReveal.createCardReveal(self.p1Suggestion)
        cr1 = cr.createNext()
        with self.assertRaises(RuntimeError):
            cr2 = cr1.createNext()

    def test_reveal_makes_note_on_suggesting_player_detective_sheet(self):
        sds = self.p1Suggestion.turn.player.getDetectiveSheet()
        siInQuestion = SheetItem.objects.get(detectiveSheet=sds, card__card_id=self.character.card_id)

        self.assertEquals(siInQuestion.checked, False)
        cr = CardReveal.createCardReveal(self.p1Suggestion)
        cr.reveal(self.character)
        siInQuestion.refresh_from_db()

        self.assertEquals(siInQuestion.checked, True)
        self.assertEquals(siInQuestion.initiallyDealt, False)
        self.assertEquals(siInQuestion.manuallyChecked, False)

    def test_endReveal_changes_status(self):
        cr = CardReveal.createCardReveal(self.p1Suggestion)
        cr.endReveal()
        cr.refresh_from_db()
        self.assertEquals(cr.status, 2)


class CaseFileModelTests(TestCase):

    def test_createRandom_is_random(self):
        #run createRandom 3 times, ensure WhoWhatWheres are not all equal (1 in 104,976 chance)
        cf1 = CaseFile.createRandom()
        cf2 = CaseFile.createRandom()
        cf3 = CaseFile.createRandom()

        self.assertEqual(cf1.compare(cf2) and cf1.compare(cf3) and cf2.compare(cf3), False)


class DetectiveSheetTests(TestCase):
    @classmethod
    def setUpClass(cls):
        #build users
        cls.user1 = User.objects.create_user('detectiveSheetUser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('detectiveSheetUser2', 'a@a.com', 'password')
        cls.user2.save()

        #build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()

        cls.g = Game()
        cls.g.initializeGame(cls.player1)
        cls.g.save()
        cls.g.addPlayer(cls.player1)
        cls.g.addPlayer(cls.player2)

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.g.delete()

    def test_makeNote_initial_deal(self):
        ds = self.player1.getDetectiveSheet()
        c = Card.objects.all()[3]
        ds.makeNote(c, True, True)

        si = SheetItem.objects.get(detectiveSheet = ds, card = c)
        self.assertEqual(si.checked, True)
        self.assertEqual(si.initiallyDealt, True)

    def test_makeNote_after_initial_deal(self):
        ds = self.player1.getDetectiveSheet()
        c = Card.objects.all()[6]
        ds.makeNote(c, True)

        si = SheetItem.objects.get(detectiveSheet = ds, card = c)
        self.assertEqual(si.checked, True)
        self.assertEqual(si.initiallyDealt, False)

    def test_makeNote_uncheck(self):
        ds = self.player1.getDetectiveSheet()
        c = Card.objects.all()[6]
        ds.makeNote(c, True)
        ds.makeNote(c, False)

        si = SheetItem.objects.get(detectiveSheet=ds, card=c)
        self.assertEqual(si.checked, False)
        self.assertEqual(si.initiallyDealt, False)

    def test_makeNote_manual_check(self):
        ds = self.player1.getDetectiveSheet()
        c = Card.objects.all()[6]
        ds.makeNote(c, True, manuallyChecked=True)

        si = SheetItem.objects.get(detectiveSheet=ds, card=c)
        self.assertEqual(si.checked, True)
        self.assertEqual(si.manuallyChecked, True)

    def test_makeNote_manual_uncheck(self):
        ds = self.player1.getDetectiveSheet()
        c = Card.objects.all()[6]
        ds.makeNote(c, True, manuallyChecked=True)

        si = SheetItem.objects.get(detectiveSheet=ds, card=c)
        self.assertEqual(si.checked, True)
        self.assertEqual(si.manuallyChecked, True)

        ds.makeNote(c, False, manuallyChecked=False)

        si = SheetItem.objects.get(detectiveSheet=ds, card=c)
        self.assertEqual(si.checked, False)
        self.assertEqual(si.manuallyChecked, False)

    def test_makeNote_regular_check_overrides_manual(self):
        ds = self.player1.getDetectiveSheet()
        c = Card.objects.all()[6]
        ds.makeNote(c, True, manuallyChecked=True)

        si = SheetItem.objects.get(detectiveSheet=ds, card=c)
        self.assertEqual(si.checked, True)
        self.assertEqual(si.manuallyChecked, True)

        ds.makeNote(c, True)

        si = SheetItem.objects.get(detectiveSheet=ds, card=c)
        self.assertEqual(si.checked, True)
        self.assertEqual(si.manuallyChecked, False)

    def test_getCharactersLeft_works_no_characters(self):
        ds = self.player1.getDetectiveSheet()
        charsLeft = ds.getCharactersLeft()
        self.assertEqual(charsLeft.count(), Character.objects.all().count())

    def test_getCharactersLeft_works_some_characters(self):
        ds = self.player1.getDetectiveSheet()
        c1 = Character.objects.all()[0]
        c2 = Character.objects.all()[3]
        ds.makeNote(c1, True)
        ds.makeNote(c2, True)

        charsLeft = ds.getCharactersLeft()
        self.assertEqual(charsLeft.count(), Character.objects.all().count() - 2)
        self.assertNotIn(c1, charsLeft)
        self.assertNotIn(c2, charsLeft)

    def test_getCharactersLeft_works_all_characters(self):
        ds = self.player1.getDetectiveSheet()
        charList = Character.objects.all()
        for c in charList:
            ds.makeNote(c, True)

        charsLeft = ds.getCharactersLeft()
        self.assertEqual(charsLeft.count(), 0)
        for c in charList:
            self.assertNotIn(c, charsLeft)

    def test_getWeaponsLeft_works_no_characters(self):
        ds = self.player1.getDetectiveSheet()
        weaponsLeft = ds.getWeaponsLeft()
        self.assertEqual(weaponsLeft.count(), Weapon.objects.all().count())

    def test_getWeaponsLeft_works_some_characters(self):
        ds = self.player1.getDetectiveSheet()
        w1 = Weapon.objects.all()[0]
        w2 = Weapon.objects.all()[3]
        ds.makeNote(w1, True)
        ds.makeNote(w2, True)

        weaponsLeft = ds.getWeaponsLeft()
        self.assertEqual(weaponsLeft.count(), Weapon.objects.all().count() - 2)
        self.assertNotIn(w1, weaponsLeft)
        self.assertNotIn(w2, weaponsLeft)

    def test_getWeaponsLeft_works_all_characters(self):
        ds = self.player1.getDetectiveSheet()
        weaponList = Weapon.objects.all()
        for w in weaponList:
            ds.makeNote(w, True)

        weaponsLeft = ds.getWeaponsLeft()
        self.assertEqual(weaponsLeft.count(), 0)
        for w in weaponList:
            self.assertNotIn(w, weaponsLeft)

    def test_getRoomsLeft_works_no_characters(self):
        ds = self.player1.getDetectiveSheet()
        roomsLeft = ds.getRoomsLeft()
        self.assertEqual(roomsLeft.count(), Room.objects.all().count())

    def test_getRoomsLeft_works_some_characters(self):
        ds = self.player1.getDetectiveSheet()
        r1 = Room.objects.all()[0]
        r2 = Room.objects.all()[3]
        ds.makeNote(r1, True)
        ds.makeNote(r2, True)

        roomsLeft = ds.getRoomsLeft()
        self.assertEqual(roomsLeft.count(), Room.objects.all().count() - 2)
        self.assertNotIn(r1, roomsLeft)
        self.assertNotIn(r2, roomsLeft)

    def test_getRoomsLeft_works_all_characters(self):
        ds = self.player1.getDetectiveSheet()
        roomList = Room.objects.all()
        for r in roomList:
            ds.makeNote(r, True)

        roomsLeft = ds.getRoomsLeft()
        self.assertEqual(roomsLeft.count(), 0)
        for r in roomList:
            self.assertNotIn(r, roomsLeft)

    def test_getCharacterSheetItems_gets_all_characters(self):
        ds = self.player1.getDetectiveSheet()
        self.assertEqual(ds.getCharacterSheetItems().count(), Character.objects.all().count())

    def test_getRoomSheetItems_gets_all_characters(self):
        ds = self.player1.getDetectiveSheet()
        self.assertEqual(ds.getRoomSheetItems().count(), Room.objects.all().count())

    def test_getWeaponSheetItems_gets_all_characters(self):
        ds = self.player1.getDetectiveSheet()
        self.assertEqual(ds.getWeaponSheetItems().count(), Weapon.objects.all().count())


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

    def test_startGame_raise_error_with_no_players(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        with self.assertRaises(RuntimeError):
            self.g.startGame(self.user1)

    def test_startGame_raise_error_with_one_player(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        with self.assertRaises(RuntimeError):
            self.g.startGame(self.user1)

    def test_startGame_raise_error_with_wrong_host(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        with self.assertRaises(RuntimeError):
            self.g.startGame(self.user2)

    def test_startGame_raise_error_when_already_started(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.status = 1
        with self.assertRaises(RuntimeError):
            self.g.startGame(self.user1)

    def test_startGame_works_with_2_players(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)

    def test_startGame_deals_all_remaining_cards(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)
        self.assertEqual(
            SheetItem.objects.filter(detectiveSheet__game = self.g, checked = True, initiallyDealt = True).count(),
            Card.objects.all().count() - 3)

    def test_startGame_doesnt_deal_casefile_cards(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)
        self.assertEqual(
            SheetItem.objects.filter(
                detectiveSheet__game = self.g,
                checked = True,
                initiallyDealt = True,
                card = self.g.caseFile.character).count(),
            0)
        self.assertEqual(
            SheetItem.objects.filter(
                detectiveSheet__game=self.g,
                checked=True,
                initiallyDealt=True,
                card=self.g.caseFile.room).count(),
            0)
        self.assertEqual(
            SheetItem.objects.filter(
                detectiveSheet__game=self.g,
                checked=True,
                initiallyDealt=True,
                card=self.g.caseFile.weapon).count(),
            0)

    def test_startGame_more_than_1_player_gets_dealt_cards(self):
        #tests a bug I identified on 12/4/2016 - JJV
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)

        p1ds = self.player1.getDetectiveSheet()
        p2ds = self.player2.getDetectiveSheet()
        self.assertGreater(
            SheetItem.objects.filter(detectiveSheet = p1ds, initiallyDealt = True, checked = True).count(),
            0)

        self.assertGreater(
            SheetItem.objects.filter(detectiveSheet=p2ds, initiallyDealt=True, checked=True).count(),
            0)

    def test_startGame_nonUserPlayers_created(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)

        self.assertEqual(Player.objects.filter(currentGame = self.g).count(), Character.objects.all().count())
        self.assertEqual(Player.objects.filter(currentGame=self.g, nonUserPlayer = True).count(), Character.objects.all().count() - 2)

    def test_startGame_currentTurn_is_set(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)

        self.assertIsNotNone(self.g.currentTurn)

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

    def test_unusedCharacters_correct_when_2_player(self):
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

    def test_registerGameUpdate_increments_game_seq(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        seq = self.g.currentSequence
        self.g.registerGameUpdate()
        self.g.save()
        self.assertEqual(seq + 1, self.g.currentSequence)

    def test_gameStateJSON_isHostPlayer_true_when_hostplayer(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)
        self.g.save()


        gsj = self.g.gameStateJSON(self.player1)
        self.assertEqual(gsj['isHostPlayer'], True)

    def test_gameStateJSON_isHostPlayer_false_when_not_hostplayer(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)
        self.g.save()

        gsj = self.g.gameStateJSON(self.player2)
        self.assertEqual(gsj['isHostPlayer'], False)

    def test_gameStateJSON_hostplayer_matches_hostplayer(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)
        self.g.save()

        gsj = self.g.gameStateJSON(self.player2)
        hp = gsj['hostplayer']
        self.assertEqual(hp['player_id'], self.player1.id)
        self.assertEqual(hp['username'], self.player1.user.username)

    def test_gameStateJSON_status_matches_game_status(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)
        self.g.save()

        self.g.status = 0
        self.g.save()
        gsj = self.g.gameStateJSON(self.player2)
        self.assertEqual(gsj['status'], 0)

        self.g.status = 1
        self.g.save()
        gsj = self.g.gameStateJSON(self.player2)
        self.assertEqual(gsj['status'], 1)

        self.g.status = 2
        self.g.save()
        gsj = self.g.gameStateJSON(self.player2)
        self.assertEqual(gsj['status'], 2)

    def test_gameStateJSON_playerstates_count_matches(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)
        self.g.save()

        gsj = self.g.gameStateJSON(self.player2)
        self.assertEqual(len(gsj['playerstates']), 6)

    def test_isAccusationCorrect_true_when_correct(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)

        cf = self.g.caseFile
        accusation = Accusation.createAccusation(self.g.currentTurn, cf.character, cf.room, cf.weapon)
        self.assertEqual(self.g.isAccusationCorrect(accusation), True)

    def test_isAccusationCorrect_false_when_incorrect_character(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)
        self.g.save()

        cf = self.g.caseFile
        cToUse = Character.objects.exclude(card_id = cf.character.card_id)[2]

        accusation = Accusation.createAccusation(self.g.currentTurn, cToUse, cf.room, cf.weapon)
        self.assertEqual(self.g.isAccusationCorrect(accusation), False)

    def test_isAccusationCorrect_false_when_incorrect_room(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)

        cf = self.g.caseFile
        rToUse = Room.objects.exclude(card_id = cf.room.card_id)[3]

        accusation = Accusation.createAccusation(self.g.currentTurn, cf.character, rToUse, cf.weapon)
        self.assertEqual(self.g.isAccusationCorrect(accusation), False)

    def test_isAccusationCorrect_false_when_incorrect_weapon(self):
        self.g.initializeGame(self.player1)
        self.g.save()
        self.g.addPlayer(self.player1)
        self.g.addPlayer(self.player2)
        self.g.startGame(self.user1)

        cf = self.g.caseFile
        wToUse = Weapon.objects.exclude(card_id = cf.weapon.card_id)[1]

        accusation = Accusation.createAccusation(self.g.currentTurn, cf.character, cf.room, wToUse)
        self.assertEqual(self.g.isAccusationCorrect(accusation), False)


class SuggestionModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        # build users
        cls.user1 = User.objects.create_user('gamestatetestuser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('gamestatetestuser2', 'a@a.com', 'password')
        cls.user2.save()
        cls.user3 = User.objects.create_user('gamestatetestuser3', 'a@a.com', 'password')
        cls.user3.save()

        # build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[2]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()
        cls.playerNotInGame = Player(user=cls.user1, character=character3, currentSpace=character3.defaultSpace)
        cls.playerNotInGame.save()

        cls.player1.currentSpace = Space.objects.get(posX=5, posY=1)

        cls.game1 = Game()
        cls.game1.initializeGame(cls.player1)
        cls.game1.save()
        cls.game1.addPlayer(cls.player1)
        cls.game1.addPlayer(cls.player2)
        cls.game1.startGame(cls.user1)

        cls.c1 = Card.objects.all()[0]

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.playerNotInGame.delete()
        cls.game1.delete()

    def test_createSuggestion_returns_saved_suggestion(self):
        turn = self.game1.currentTurn
        character = Character.objects.all()[0]
        room = Room.objects.get(id=self.player1.currentSpace.spaceCollector.id)
        weapon = Weapon.objects.all()[0]

        newSuggestion = Suggestion.createSuggestion(turn, character, room, weapon)
        self.assertIsNotNone(newSuggestion.id)

    def test_validate_false_wrong_room(self):
        turn = self.game1.currentTurn
        character = Character.objects.all()[0]
        room = Room.objects.exclude(id=self.player1.currentSpace.spaceCollector.id)[0]
        weapon = Weapon.objects.all()[0]

        newSuggestion = Suggestion.createSuggestion(turn, character, room, weapon)
        self.assertEqual(newSuggestion.validate(), False)

    def test_validate_true_correct_room(self):
        turn = self.game1.currentTurn
        character = Character.objects.all()[0]
        room = Room.objects.get(id=self.player1.currentSpace.spaceCollector.id)
        weapon = Weapon.objects.all()[0]

        newSuggestion = Suggestion.createSuggestion(turn, character, room, weapon)
        self.assertEqual(newSuggestion.validate(), True)

    def test_performAction_move_suggested_player(self):
        turn = self.game1.currentTurn
        character = Character.objects.all()[0]
        room = Room.objects.get(id=self.player1.currentSpace.spaceCollector.id)
        weapon = Weapon.objects.all()[0]

        newSuggestion = Suggestion.createSuggestion(turn, character, room, weapon)
        newSuggestion.performAction()
        movedPlayer = Player.objects.get(currentGame=self.game1, character=character)
        self.assertEqual(movedPlayer.currentSpace, self.player1.currentSpace)


class AccusationModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        # build users
        cls.user1 = User.objects.create_user('gamestatetestuser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('gamestatetestuser2', 'a@a.com', 'password')
        cls.user2.save()
        cls.user3 = User.objects.create_user('gamestatetestuser3', 'a@a.com', 'password')
        cls.user3.save()

        # build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[2]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()
        cls.playerNotInGame = Player(user=cls.user1, character=character3, currentSpace=character3.defaultSpace)
        cls.playerNotInGame.save()

        cls.player1.currentSpace = Space.objects.get(posX=5, posY=1)

        cls.game1 = Game()
        cls.game1.initializeGame(cls.player1)
        cls.game1.save()
        cls.game1.addPlayer(cls.player1)
        cls.game1.addPlayer(cls.player2)
        cls.game1.startGame(cls.user1)

        cls.c1 = Card.objects.all()[0]

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.playerNotInGame.delete()
        cls.game1.delete()

    def test_createAccusation_returns_saved_suggestion(self):
        turn = self.game1.currentTurn
        character = Character.objects.all()[0]
        room = Room.objects.all()[3]
        weapon = Weapon.objects.all()[0]

        newAcc = Accusation.createAccusation(turn, character, room, weapon)
        self.assertIsNotNone(newAcc.id)

    def test_takeAction_correct_player_wins(self):
        turn = self.game1.currentTurn
        character = self.game1.caseFile.character
        room = self.game1.caseFile.room
        weapon = self.game1.caseFile.weapon

        newAcc = Accusation.createAccusation(turn, character, room, weapon)
        turn.takeAction(newAcc)
        self.assertEquals(Player.objects.get(id = turn.player.id).gameResult, 1)

    def test_takeAction_incorrect_player_loses(self):
        turn = self.game1.currentTurn
        character = self.game1.caseFile.character
        goodRoom = self.game1.caseFile.room
        weapon = self.game1.caseFile.weapon
        room = Room.objects.exclude(card_id = goodRoom.card_id)[3]

        newAcc = Accusation.createAccusation(turn, character, room, weapon)
        turn.takeAction(newAcc)
        self.assertEquals(Player.objects.get(id = turn.player.id).gameResult, -1)

    def test_takeAction_correct_game_is_over(self):
        turn = self.game1.currentTurn
        character = self.game1.caseFile.character
        room = self.game1.caseFile.room
        weapon = self.game1.caseFile.weapon

        newAcc = Accusation.createAccusation(turn, character, room, weapon)
        turn.takeAction(newAcc)
        self.assertEquals(Game.objects.get(id = turn.game.id).status, 2)


class TurnModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        # build users
        cls.user1 = User.objects.create_user('gamestatetestuser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('gamestatetestuser2', 'a@a.com', 'password')
        cls.user2.save()
        cls.user3 = User.objects.create_user('gamestatetestuser3', 'a@a.com', 'password')
        cls.user3.save()

        # build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[2]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()
        cls.playerNotInGame = Player(user=cls.user1, character=character3, currentSpace=character3.defaultSpace)
        cls.playerNotInGame.save()

        cls.player1.currentSpace = Space.objects.get(posX=5, posY=1)

        cls.game1 = Game()
        cls.game1.initializeGame(cls.player1)
        cls.game1.save()
        cls.game1.addPlayer(cls.player1)
        cls.game1.addPlayer(cls.player2)
        cls.game1.startGame(cls.user1)

        cls.c1 = Card.objects.all()[0]

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.playerNotInGame.delete()
        cls.game1.delete()

    def test_takeAction_on_accusation_error_when_previous_accusation(self):
        turn = self.game1.currentTurn
        www = WhoWhatWhere(
            character=Character.objects.all()[0],
            room=Room.objects.all()[0],
            weapon=Weapon.objects.all()[0],
        )
        www.save()
        prevAccusation = Accusation(turn=turn, whoWhatWhere=www)
        prevAccusation.save()
        newAccusation = Accusation(turn=turn, whoWhatWhere=www)
        newAccusation.save()
        self.assertIsNotNone(turn.takeAction(newAccusation))

    def test_takeAction_on_valid_accusation_no_error(self):
        turn = self.game1.currentTurn
        www = WhoWhatWhere(
            character=Character.objects.all()[0],
            room=Room.objects.all()[0],
            weapon=Weapon.objects.all()[0],
        )
        www.save()
        newAccusation = Accusation(turn=turn, whoWhatWhere=www)
        newAccusation.save()
        self.assertIsNone(turn.takeAction(newAccusation))

    def test_takeAction_on_suggestion_error_when_previous_accusation(self):
        turn = self.game1.currentTurn
        www = WhoWhatWhere(
            character=Character.objects.all()[0],
            room=Room.objects.all()[0],
            weapon=Weapon.objects.all()[0],
        )
        www.save()
        prevAccusation = Accusation(turn=turn, whoWhatWhere=www)
        prevAccusation.save()
        newSuggestion = Suggestion.createSuggestion(turn, www.character, www.room, www.weapon)
        self.assertIsNotNone(turn.takeAction(newSuggestion))

    def test_takeAction_on_suggestion_error_when_previous_suggestion(self):
        turn = self.game1.currentTurn
        www = WhoWhatWhere(
            character=Character.objects.all()[0],
            room=Room.objects.all()[0],
            weapon=Weapon.objects.all()[0],
        )
        www.save()
        prevSuggestion = Suggestion.createSuggestion(turn, www.character, www.room, www.weapon)
        newSuggestion = Suggestion.createSuggestion(turn, www.character, www.room, www.weapon)
        self.assertIsNotNone(turn.takeAction(newSuggestion))

    def test_takeAction_on_valid_suggestion_no_error(self):
        turn = self.game1.currentTurn
        character = Character.objects.all()[0]
        room = Room.objects.get(id=self.player1.currentSpace.spaceCollector.id)
        weapon = Weapon.objects.all()[0]

        newSuggestion = Suggestion.createSuggestion(turn, character, room, weapon)
        self.assertIsNone(turn.takeAction(newSuggestion))

    def test_takeAction_on_move_error_when_previous_accusation(self):
        turn = self.game1.currentTurn
        www = WhoWhatWhere(
            character=Character.objects.all()[0],
            room=Room.objects.all()[0],
            weapon=Weapon.objects.all()[0],
        )
        www.save()
        prevAccusation = Accusation(turn=turn, whoWhatWhere=www)
        prevAccusation.save()
        newMove = Move(turn=turn, fromSpace=self.player1.currentSpace, toSpace=Space.objects.get(posX=5, posY=2))
        newMove.save()
        self.assertIsNotNone(turn.takeAction(newMove))

    def test_takeAction_on_move_error_when_previous_suggestion(self):
        turn = self.game1.currentTurn
        www = WhoWhatWhere(
            character=Character.objects.all()[0],
            room=Room.objects.all()[0],
            weapon=Weapon.objects.all()[0],
        )
        www.save()
        newSuggestion = Suggestion.createSuggestion(turn, www.character, www.room, www.weapon)
        newMove = Move(turn=turn, fromSpace=self.player1.currentSpace, toSpace=Space.objects.get(posX=5, posY=2))
        newMove.save()
        self.assertIsNotNone(turn.takeAction(newMove))

    def test_takeAction_on_move_error_when_previous_move(self):
        turn = self.game1.currentTurn
        prevMove = Move(turn=turn, fromSpace=self.player1.currentSpace, toSpace=Space.objects.get(posX=5, posY=2))
        prevMove.save()
        turn.takeAction(prevMove)
        newMove = Move(turn=turn, fromSpace=self.player1.currentSpace, toSpace=Space.objects.get(posX=5, posY=3))
        newMove.save()
        self.assertIsNotNone(turn.takeAction(newMove))

    def test_takeAction_on_move_no_error(self):
        turn = self.game1.currentTurn
        newMove = Move(turn=turn, fromSpace=self.player1.currentSpace, toSpace=Space.objects.get(posX=5, posY=2))
        newMove.save()
        self.assertIsNone(turn.takeAction(newMove))

    def test_takeAction_performs_valid_action(self):
        turn = self.game1.currentTurn
        character = Character.objects.all()[0]
        room = Room.objects.get(id=self.player1.currentSpace.spaceCollector.id)
        weapon = Weapon.objects.all()[0]

        newSuggestion = Suggestion.createSuggestion(turn, character, room, weapon)
        self.assertIsNone(turn.takeAction(newSuggestion))
        movedPlayer = Player.objects.get(currentGame=self.game1, character=character)
        self.assertEqual(movedPlayer.currentSpace, self.player1.currentSpace)


class WhoWhatWhereModelTests(TestCase):

    def test_compare_true_when_equal(self):
        c1 = Character.objects.all()[0]
        r1 = Room.objects.all()[3]
        w1 = Weapon.objects.all()[2]
        c2 = Character.objects.all()[0]
        r2 = Room.objects.all()[3]
        w2 = Weapon.objects.all()[2]

        www1 = WhoWhatWhere(character = c1, room = r1, weapon = w1)
        www2 = WhoWhatWhere(character = c2, room = r2, weapon = w2)

        self.assertEqual(www1.compare(www2), True)
        self.assertEqual(www2.compare(www1), True)

    def test_compare_false_when_all_not_equal(self):
        c1 = Character.objects.all()[0]
        r1 = Room.objects.all()[3]
        w1 = Weapon.objects.all()[2]
        c2 = Character.objects.all()[1]
        r2 = Room.objects.all()[5]
        w2 = Weapon.objects.all()[3]

        www1 = WhoWhatWhere(character = c1, room = r1, weapon = w1)
        www2 = WhoWhatWhere(character = c2, room = r2, weapon = w2)

        self.assertEqual(www1.compare(www2), False)
        self.assertEqual(www2.compare(www1), False)

    def test_compare_false_when_character_not_equal(self):
        c1 = Character.objects.all()[0]
        r1 = Room.objects.all()[3]
        w1 = Weapon.objects.all()[2]
        c2 = Character.objects.all()[1]
        r2 = Room.objects.all()[3]
        w2 = Weapon.objects.all()[2]

        www1 = WhoWhatWhere(character = c1, room = r1, weapon = w1)
        www2 = WhoWhatWhere(character = c2, room = r2, weapon = w2)

        self.assertEqual(www1.compare(www2), False)
        self.assertEqual(www2.compare(www1), False)

    def test_compare_false_when_room_not_equal(self):
        c1 = Character.objects.all()[0]
        r1 = Room.objects.all()[2]
        w1 = Weapon.objects.all()[2]
        c2 = Character.objects.all()[0]
        r2 = Room.objects.all()[3]
        w2 = Weapon.objects.all()[2]

        www1 = WhoWhatWhere(character = c1, room = r1, weapon = w1)
        www2 = WhoWhatWhere(character = c2, room = r2, weapon = w2)

        self.assertEqual(www1.compare(www2), False)
        self.assertEqual(www2.compare(www1), False)

    def test_compare_false_when_weapon_not_equal(self):
        c1 = Character.objects.all()[0]
        r1 = Room.objects.all()[3]
        w1 = Weapon.objects.all()[3]
        c2 = Character.objects.all()[0]
        r2 = Room.objects.all()[3]
        w2 = Weapon.objects.all()[2]

        www1 = WhoWhatWhere(character = c1, room = r1, weapon = w1)
        www2 = WhoWhatWhere(character = c2, room = r2, weapon = w2)

        self.assertEqual(www1.compare(www2), False)
        self.assertEqual(www2.compare(www1), False)


#tests for views

class DetectiveSheetViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # get client
        cls.c = Client()
        # build users
        cls.user1 = User.objects.create_user('gamestatetestuser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('gamestatetestuser2', 'a@a.com', 'password')
        cls.user2.save()
        cls.user3 = User.objects.create_user('gamestatetestuser3', 'a@a.com', 'password')
        cls.user3.save()

        # build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[2]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()
        cls.playerNotInGame = Player(user=cls.user1, character=character3, currentSpace=character3.defaultSpace)
        cls.playerNotInGame.save()

        cls.game1 = Game()
        cls.game1.initializeGame(cls.player1)
        cls.game1.save()
        cls.game1.addPlayer(cls.player1)
        cls.game1.addPlayer(cls.player2)

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.playerNotInGame.delete()
        cls.game1.delete()

    def test_user_must_be_logged_in(self):
        url = reverse('detectivesheet', args=[self.game1.id, self.player1.id])
        response = self.c.get(url)
        self.assertRegex(response.url, 'login')

    def test_fail_bad_game_id(self):
        url = reverse('detectivesheet', args=[0, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_player_id(self):
        url = reverse('detectivesheet', args=[self.game1.id, 0])
        self.c.force_login(self.user1)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 422)

    def test_fail_player_not_in_game_redirects(self):
        url = reverse('detectivesheet', args=[self.game1.id, self.playerNotInGame.id])
        response = self.c.get(url)
        self.assertEqual(response.status_code, 302)

    def test_fail_user_doesnt_match_player(self):
        url = reverse('detectivesheet', args=[self.game1.id, self.player2.id])
        self.c.force_login(self.user1)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 403)

    def test_view_runs(self):
        url = reverse('detectivesheet', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)


class GameStateViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        #get client
        cls.c = Client()
        #build users
        cls.user1 = User.objects.create_user('gamestatetestuser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('gamestatetestuser2', 'a@a.com', 'password')
        cls.user2.save()
        cls.user3 = User.objects.create_user('gamestatetestuser3', 'a@a.com', 'password')
        cls.user3.save()

        #build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[2]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()
        cls.playerNotInGame = Player(user=cls.user1, character=character3, currentSpace=character3.defaultSpace)
        cls.playerNotInGame.save()
        cls.playerNotInGameAndNotUser = Player(user=cls.user3, character=character3, currentSpace=character3.defaultSpace)
        cls.playerNotInGameAndNotUser.save()

        cls.game1 = Game()
        cls.game1.initializeGame(cls.player1)
        cls.game1.save()
        cls.game1.addPlayer(cls.player1)
        cls.game1.addPlayer(cls.player2)
        cls.game1.startGame(cls.user1)
        cls.game1.save()

        cls.gsUrl = reverse('gamestate')

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.playerNotInGame.delete()
        cls.playerNotInGameAndNotUser.delete()
        cls.game1.delete()


    def test_user_must_be_logged_in(self):
        response = self.c.post(self.gsUrl, {})
        self.assertRegex(response.url, 'login')

    def test_not_post_not_allowed(self):
        self.c.force_login(self.user1)
        response = self.c.get(self.gsUrl)
        self.assertEqual(response.status_code, 417)

    def test_fail_no_parameters_sent(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl, {})
        self.assertEqual(response.status_code, 417)

    def test_fail_game_id_parameter_not_sent(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl,
                               {'player_id': self.player1.id, 'cached_game_seq': self.game1.currentSequence})
        self.assertEqual(response.status_code, 417)

    def test_fail_player_id_parameter_not_sent(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl,
                               {'game_id': self.game1.id, 'cached_game_seq': self.game1.currentSequence})
        self.assertEqual(response.status_code, 417)

    def test_fail_cached_game_seq_parameter_not_sent(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl, {})
        response = self.c.post(self.gsUrl,
                               {'game_id': self.game1.id, 'player_id': self.player1.id})
        self.assertEqual(response.status_code, 417)

    def test_fail_bad_game_id(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl,
                               {'game_id': -1,
                                'player_id': self.player1.id,
                                'cached_game_seq': self.game1.currentSequence})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_player_id(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl,
                               {'game_id': self.game1.id,
                                'player_id': -1,
                                'cached_game_seq': self.game1.currentSequence})
        self.assertEqual(response.status_code, 422)

    def test_fail_user_doesnt_match_player(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl,
                               {'game_id': self.game1.id,
                                'player_id': self.player2.id,
                                'cached_game_seq': self.game1.currentSequence})
        self.assertEqual(response.status_code, 403)

    def test_fail_player_not_in_game(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl,
                               {'game_id': self.game1.id,
                                'player_id': self.playerNotInGame.id,
                                'cached_game_seq': self.game1.currentSequence})
        self.assertEqual(response.status_code, 403)

    def test_changed_is_false_when_cache_matches(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl,
                               {'game_id': self.game1.id,
                                'player_id': self.player1.id,
                                'cached_game_seq': (self.game1.currentSequence)})
        responseJSON = json.loads(response.content)
        self.assertEqual(responseJSON['changed'], False)

    def test_changed_is_true_when_cache_doesnt_match(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl,
                               {'game_id': self.game1.id,
                                'player_id': self.player1.id,
                                'cached_game_seq': (self.game1.currentSequence-1)})
        responseJSON = json.loads(response.content)
        self.assertEqual(responseJSON['changed'], True)

    def test_gameStateJSON_present_when_cache_doesnt_match(self):
        self.c.force_login(self.user1)
        response = self.c.post(self.gsUrl,
                               {'game_id': self.game1.id,
                                'player_id': self.player1.id,
                                'cached_game_seq': (self.game1.currentSequence-1)})
        responseJSON = json.loads(response.content)
        self.assertIn('gamestate', responseJSON.keys())


class ManualSheetItemCheckViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # get client
        cls.c = Client()
        # build users
        cls.user1 = User.objects.create_user('gamestatetestuser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('gamestatetestuser2', 'a@a.com', 'password')
        cls.user2.save()
        cls.user3 = User.objects.create_user('gamestatetestuser3', 'a@a.com', 'password')
        cls.user3.save()

        # build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[2]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()
        cls.playerNotInGame = Player(user=cls.user1, character=character3, currentSpace=character3.defaultSpace)
        cls.playerNotInGame.save()

        cls.game1 = Game()
        cls.game1.initializeGame(cls.player1)
        cls.game1.save()
        cls.game1.addPlayer(cls.player1)
        cls.game1.addPlayer(cls.player2)
        cls.game1.startGame(cls.user1)

        cls.c1 = Card.objects.all()[0]

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.playerNotInGame.delete()
        cls.game1.delete()

    def test_user_must_be_logged_in(self):
        url = reverse('manualsheetitemcheck', args=[self.game1.id, self.player1.id])
        response = self.c.post(url, {'card_id':self.c1.card_id, 'check':1})
        self.assertEqual(response.status_code, 403)

    def test_not_post_not_allowed(self):
        url = reverse('manualsheetitemcheck', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.get(url, {'card_id': self.c1.card_id, 'check': 1})
        self.assertEqual(response.status_code, 417)

    def test_fail_no_parameters_sent(self):
        url = reverse('manualsheetitemcheck', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {})
        self.assertEqual(response.status_code, 417)

    def test_fail_cached_card_id_parameter_not_sent(self):
        url = reverse('manualsheetitemcheck', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'check': 1})
        self.assertEqual(response.status_code, 417)

    def test_fail_cached_check_parameter_not_sent(self):
        url = reverse('manualsheetitemcheck', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'card_id': self.c1.card_id})
        self.assertEqual(response.status_code, 417)

    def test_fail_bad_game_id(self):
        url = reverse('manualsheetitemcheck', args=[0, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'card_id': self.c1.card_id, 'check':1})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_player_id(self):
        url = reverse('manualsheetitemcheck', args=[self.game1.id, 0])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'card_id': self.c1.card_id, 'check': 1})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_card_id(self):
        url = reverse('manualsheetitemcheck', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'card_id': 0, 'check': 1})
        self.assertEqual(response.status_code, 422)

    def test_fail_user_doesnt_match_player(self):
        url = reverse('manualsheetitemcheck', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user2)
        response = self.c.post(url, {'card_id': self.c1.card_id, 'check': 1})
        self.assertEqual(response.status_code, 403)

    def test_fail_player_not_in_game(self):
        url = reverse('manualsheetitemcheck', args=[self.game1.id, self.playerNotInGame.id])
        self.c.force_login(self.user3)
        response = self.c.post(url, {'card_id': self.c1.card_id, 'check': 1})
        self.assertEqual(response.status_code, 403)

    def test_manual_checked_works(self):
        exampleCard = SheetItem.objects.filter(
            detectiveSheet = self.player1.getDetectiveSheet(),
            checked = False,
            manuallyChecked = False
        )[0].card


        url = reverse('manualsheetitemcheck', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'card_id': exampleCard.card_id, 'check': 1})
        self.assertEqual(response.status_code, 200)

        si = SheetItem.objects.filter(
            detectiveSheet=self.player1.getDetectiveSheet(),
            checked=True,
            manuallyChecked=True,
            card = exampleCard
        )

        self.assertEqual(si.count(), 1)

    def test_manual_uncheck_works(self):
        exampleSI = SheetItem.objects.filter(
            detectiveSheet=self.player1.getDetectiveSheet(),
            checked = False,
            initiallyDealt = False
        )[0]

        exampleSI.checked = True
        exampleSI.manuallyChecked = True
        exampleSI.save()


        url = reverse('manualsheetitemcheck', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'card_id': exampleSI.card.card_id, 'check': 0})
        self.assertEqual(response.status_code, 200)

        si = SheetItem.objects.filter(
            detectiveSheet=self.player1.getDetectiveSheet(),
            checked=False,
            manuallyChecked=True,
            card=exampleSI.card.card_id
        )

        self.assertEqual(si.count(), 1)


class PlayGameViewTest(TestCase):

    @classmethod
    def setUpClass(cls):
        #get client
        cls.c = Client()
        #build users
        cls.user1 = User.objects.create_user('gamestatetestuser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('gamestatetestuser2', 'a@a.com', 'password')
        cls.user2.save()
        cls.user3 = User.objects.create_user('gamestatetestuser3', 'a@a.com', 'password')
        cls.user3.save()

        #build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[2]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()
        cls.playerNotInGame = Player(user=cls.user1, character=character3, currentSpace=character3.defaultSpace)
        cls.playerNotInGame.save()

        cls.game1 = Game()
        cls.game1.initializeGame(cls.player1)
        cls.game1.save()
        cls.game1.addPlayer(cls.player1)
        cls.game1.addPlayer(cls.player2)

        cls.gsUrl = reverse('gamestate')

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.playerNotInGame.delete()
        cls.game1.delete()


    def test_user_must_be_logged_in(self):
        url = reverse('playgame', args=[self.game1.id])
        response = self.c.get(url)
        self.assertRegex(response.url, 'login')

    def test_fail_bad_game_id(self):
        url = reverse('playgame', args=[0])
        self.c.force_login(self.user1)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 422)

    def test_fail_user_not_in_game(self):
        url = reverse('playgame', args=[self.game1.id])
        self.c.force_login(self.user3)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 422)

    def test_game_not_started_redirects_to_begingame(self):
        self.game1.status = 0
        self.game1.save()

        url = reverse('playgame', args=[self.game1.id])
        self.c.force_login(self.user1)
        response = self.c.get(url)
        self.assertEqual(response.url, reverse('begingame', args=[self.game1.id]))


#tests for controller views

class MakeSuggestionControllerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # get client
        cls.c = Client()
        # build users
        cls.user1 = User.objects.create_user('gamestatetestuser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('gamestatetestuser2', 'a@a.com', 'password')
        cls.user2.save()
        cls.user3 = User.objects.create_user('gamestatetestuser3', 'a@a.com', 'password')
        cls.user3.save()

        # build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[2]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()
        cls.playerNotInGame = Player(user=cls.user1, character=character3, currentSpace=character3.defaultSpace)
        cls.playerNotInGame.save()

        cls.player1.currentSpace = Space.objects.get(posX=5, posY=1)

        cls.game1 = Game()
        cls.game1.initializeGame(cls.player1)
        cls.game1.save()
        cls.game1.addPlayer(cls.player1)
        cls.game1.addPlayer(cls.player2)
        cls.game1.startGame(cls.user1)

        cls.c1 = Card.objects.all()[0]

        cls.character = Character.objects.all()[0]
        cls.goodRoom = Room.objects.get(id=cls.player1.currentSpace.spaceCollector.id)
        cls.weapon = Weapon.objects.all()[0]

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.playerNotInGame.delete()
        cls.game1.delete()

    def test_user_must_be_logged_in(self):
        url = reverse('make_suggestion_controller',args=[self.game1.id,self.player1.id])
        response = self.c.post(url, {'suspect_id':self.character.card_id, 'room_id':self.goodRoom.card_id, 'weapon_id':self.weapon.card_id})
        self.assertEqual(response.status_code, 403)

    def test_not_post_not_allowed(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.get(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 417)

    def test_fail_no_parameters_sent(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {})

        self.assertEqual(response.status_code, 417)

    def test_fail_suspect_id_parameter_not_sent(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'room_id': self.goodRoom.card_id, 'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 417)

    def test_fail_room_id_parameter_not_sent(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 417)

    def test_fail_weapon_id_parameter_not_sent(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id})
        self.assertEqual(response.status_code, 417)

    def test_fail_bad_game_id(self):
        url = reverse('make_suggestion_controller', args=[0, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_player_id(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, 0])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_suspect_id(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': 0, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_room_id(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': 0,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_weapon_id(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': 0})
        self.assertEqual(response.status_code, 422)

    def test_fail_user_doesnt_match_player(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user2)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 403)

    def test_fail_player_not_in_game(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.playerNotInGame.id])
        self.c.force_login(self.user3)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 403)

    def test_fail_not_players_turn(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player2.id])
        self.c.force_login(self.user2)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 403)

    def test_fail_wrong_room(self):
        badRoom = Room.objects.exclude(id=self.player1.currentSpace.spaceCollector.id)[0]

        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': badRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 500)

    def test_create_suggestion_when_valid(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(Suggestion.objects.filter(turn = self.game1.currentTurn).count(), 1)

    def test_increment_game_state_when_valid(self):
        cachedState = self.game1.currentSequence
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertNotEqual(cachedState, Game.objects.get(id = self.game1.id).currentSequence)

    def test_produce_http200_when_valid(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.character.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.weapon.card_id})
        self.assertEqual(response.status_code, 200)


class MakeAccusationControllerTest(TestCase):

    @classmethod
    def setUpClass(cls):
        # get client
        cls.c = Client()
        # build users
        cls.user1 = User.objects.create_user('gamestatetestuser1', 'a@a.com', 'password')
        cls.user1.save()
        cls.user2 = User.objects.create_user('gamestatetestuser2', 'a@a.com', 'password')
        cls.user2.save()
        cls.user3 = User.objects.create_user('gamestatetestuser3', 'a@a.com', 'password')
        cls.user3.save()

        # build some players
        character1 = Character.objects.all()[0]
        character2 = Character.objects.all()[1]
        character3 = Character.objects.all()[2]
        cls.player1 = Player(user=cls.user1, character=character1, currentSpace=character1.defaultSpace)
        cls.player1.save()
        cls.player2 = Player(user=cls.user2, character=character2, currentSpace=character2.defaultSpace)
        cls.player2.save()
        cls.playerNotInGame = Player(user=cls.user1, character=character3, currentSpace=character3.defaultSpace)
        cls.playerNotInGame.save()

        cls.player1.currentSpace = Space.objects.get(posX=5, posY=1)

        cls.game1 = Game()
        cls.game1.initializeGame(cls.player1)
        cls.game1.save()
        cls.game1.addPlayer(cls.player1)
        cls.game1.addPlayer(cls.player2)
        cls.game1.startGame(cls.user1)

        cls.goodCharacter = cls.game1.caseFile.character
        cls.goodRoom = cls.game1.caseFile.room
        cls.goodWeapon = cls.game1.caseFile.weapon

        cls.wrongCharacter = Character.objects.exclude(card_id = cls.goodCharacter.card_id)

    @classmethod
    def tearDownClass(cls):
        cls.c = None
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()
        cls.player1.delete()
        cls.player2.delete()
        cls.playerNotInGame.delete()
        cls.game1.delete()

    def test_user_must_be_logged_in(self):
        url = reverse('make_accusation_controller',args=[self.game1.id,self.player1.id])
        response = self.c.post(url, {'suspect_id':self.goodCharacter.card_id, 'room_id':self.goodRoom.card_id, 'weapon_id':self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 403)

    def test_not_post_not_allowed(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.get(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 417)

    def test_fail_no_parameters_sent(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {})

        self.assertEqual(response.status_code, 417)

    def test_fail_suspect_id_parameter_not_sent(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 417)

    def test_fail_room_id_parameter_not_sent(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 417)

    def test_fail_weapon_id_parameter_not_sent(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': self.goodRoom.card_id})
        self.assertEqual(response.status_code, 417)

    def test_fail_bad_game_id(self):
        url = reverse('make_accusation_controller', args=[0, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_player_id(self):
        url = reverse('make_suggestion_controller', args=[self.game1.id, 0])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_suspect_id(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': 0, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_room_id(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': 0,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 422)

    def test_fail_bad_weapon_id(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': 0})
        self.assertEqual(response.status_code, 422)

    def test_fail_user_doesnt_match_player(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user2)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 403)

    def test_fail_player_not_in_game(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.playerNotInGame.id])
        self.c.force_login(self.user3)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 403)

    def test_fail_not_players_turn(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player2.id])
        self.c.force_login(self.user2)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 403)

    def test_increment_game_state_when_valid(self):
        cachedState = self.game1.currentSequence
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertNotEqual(cachedState, Game.objects.get(id = self.game1.id).currentSequence)

    def test_produce_http200_when_valid(self):
        url = reverse('make_accusation_controller', args=[self.game1.id, self.player1.id])
        self.c.force_login(self.user1)
        response = self.c.post(url, {'suspect_id': self.goodCharacter.card_id, 'room_id': self.goodRoom.card_id,
                                     'weapon_id': self.goodWeapon.card_id})
        self.assertEqual(response.status_code, 200)
