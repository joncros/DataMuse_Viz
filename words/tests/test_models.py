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

    def test_object_string(self):
        word = Word.objects.get(name="apple")
        expected_object_name = "apple"
        self.assertEqual(expected_object_name, str(word))

    def test_default_language(self):
        word = Word.objects.get(name="apple")
        expected_object_language = 'en'
        self.assertEqual(expected_object_language, word.language.name)


class LanguageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        # Language.objects.create()
        Word.objects.create(name="apple")

    def test_object_string_is_verbose(self):
        lang = Word.objects.get(name='apple').language
        expected_object_string = "English"
        self.assertEqual(expected_object_string, str(lang))


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
        WordSet.objects.create(name="Test Set 1", creator=test_user)
        WordSet.objects.create(name="Test Set 2")

    def test_object_name(self):
        set = WordSet.objects.get(name="Test Set 1")
        expected_object_name = "Test Set 1 (created by testuser)"
        self.assertEqual(expected_object_name, str(set))

    def test_object_name_with_no_creator(self):
        set = WordSet.objects.get(name="Test Set 2")
        expected_object_name = "Test Set 2"
        self.assertEqual(expected_object_name, str(set))

