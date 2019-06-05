from django.core.exceptions import ValidationError
from django.db import IntegrityError
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

    def test_uppercase_characters_in_name_converted_to_lowercase(self):
        word = Word.objects.create(name="walKABOUT")
        expected_object_name = 'walkabout'
        self.assertEqual(word.name, expected_object_name)

    def test_object_search_ignores_case(self):
        word1 = Word.objects.get(name="APple")
        word2 = Word.objects.get(name="apple")
        self.assertEqual(word1, word2)

    def test_word_create_with_duplicate_name(self):
        with self.assertRaises(IntegrityError):
            Word.objects.create(name="apple")

    def test_language_deletion_prevented_if_words_in_language_exist(self):
        with self.assertRaises(IntegrityError):
            Language.objects.get(name="en").delete()

    def test_relation_fields_not_symmetrical(self):
        """Tests all fields holding words related to the Word to ensure symmetrical attribute is false"""
        relation_field_names = [
            'jja',
            'jjb',
            'syn',
            'trg',
            'ant',
            'spc',
            'gen',
            'com',
            'par',
            'bga',
            'bgb',
            'rhy',
            'nry',
            'hom',
            'cns',
        ]

        word1 = Word.objects.create(name="dog")
        word2 = Word.objects.create(name="canine")
        for name in relation_field_names:
            # add word2 to the field in word1
            word1_field = getattr(word1, name)
            word1_field.add(word2)

            # get same field in word2, fail if it contains word1
            word2_field = getattr(word2, name)
            self.assertFalse(word2_field.filter(name="dog").exists(), msg=f'field {name} not symmetrical')


class LanguageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        # Language.objects.create()
        Word.objects.create(name="apple")
        Language.objects.create(name="es")

    def test_object_string_is_verbose(self):
        lang = Word.objects.get(name='apple').language
        expected_object_string = "English"
        self.assertEqual(expected_object_string, str(lang))

    def test_language_pk_is_unique(self):
        """Tests that there is only ever one instance per language string"""
        Word.objects.create(name="orange")
        Word.objects.create(name="hasta", language=Language("es"))
        self.assertEqual(Language.objects.count(), 2)
        with self.assertRaises(IntegrityError):
            Language.objects.create(name="es")


class PartOfSpeechTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        PartOfSpeech.objects.create(name="adj")

    def test_object_string(self):
        part = PartOfSpeech.objects.get(name="adj")
        expected_object_name = "adjective"
        self.assertEqual(expected_object_name, str(part))

    def test_object_pk_unique(self):
        """Test there can never be more than one instance of a PartOfSpeech with a given name"""
        with self.assertRaises(IntegrityError):
            PartOfSpeech.objects.create(name="adj")


class WordSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        test_user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK')
        WordSet.objects.create(name="Test Set 1", creator=test_user)
        WordSet.objects.create(name="Test Set 2")

    def test_object_name(self):
        word_set = WordSet.objects.get(name="Test Set 1")
        expected_object_name = "Test Set 1 (created by testuser)"
        self.assertEqual(expected_object_name, str(word_set))

    def test_object_name_with_no_creator(self):
        word_set = WordSet.objects.get(name="Test Set 2")
        expected_object_name = f'Test Set 2 ({word_set.id})'
        self.assertEqual(expected_object_name, str(word_set))

    def test_unique_wordset_name_per_creator(self):
        test_user = User.objects.get(username='testuser')
        with self.assertRaises(IntegrityError):
            WordSet.objects.create(name="Test Set 1", creator=test_user, description="one")

    def test_absolute_url(self):
        word_set = WordSet.objects.get(name="Test Set 1")
        pk = word_set.id
        expected_url = f'/words/wordset/{pk}'
        self.assertEqual(word_set.get_absolute_url(), expected_url)
