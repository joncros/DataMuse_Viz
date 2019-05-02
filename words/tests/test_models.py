from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User

from words.models import Word, Language, PartOfSpeech, WordSet

class WordTest(TestCase):
    """Tests model class Word"""

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Word.objects.create(name="apple")

    def test_object_name(self):
        word = Word.objects.get(id=1)
        expected_object_name = "apple"
        self.assertEqual(expected_object_name, str(word))


class LanguageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Language.objects.create()

    def test_object_name(self):
        lang = Language.objects.get(id=1)
        expected_object_name = "English"
        self.assertEqual(expected_object_name, str(lang))

class PartOfSpeechTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        PartOfSpeech.objects.create(name="adj")

    def test_object_name(self):
        part = PartOfSpeech.objects.get(name="adj")
        expected_object_name = "adjective"
        self.assertEqual(expected_object_name, str(part))

class WordSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        test_user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK')
        WordSet.objects.create(name="Test Set 1", owner=test_user)

    def test_object_name(self):
        set = WordSet.objects.get(name="Test Set 1")
        expected_object_name = "Test Set 1 (created by testuser)"
        self.assertEqual(expected_object_name, str(set))

    def test_error_if_create_private_wordset_with_blank_owner(self):
        # Should fail if ValidationError is not raised
        with self.assertRaises(ValidationError):
            WordSet.objects.create(name="Test Set 2", private=True)

    def test_error_if_wordset_without_owner_set_to_private(self):
        wset = WordSet.objects.create(name="Test Set 2")
        with self.assertRaises(ValidationError):
            wset.private = True
            wset.save()

    def test_deleting_user_should_delete_owned_private_wordsets(self):
        test_user2 = User.objects.create_user(username='testuser2', password='kw+tuK1X<ISRU')
        WordSet.objects.create(name="Test Set 2", owner=test_user2, private=True)
        test_user2.delete()
        exists = WordSet.objects.filter(name="Test Set 2").exists()
        self.assertFalse(exists)

