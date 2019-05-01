from django.test import TestCase
from words.models import Word, Language, PartOfSpeech

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