import unittest.mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from words.datamuse_json import add_or_update_word, add_related, query_with_retry
from words.models import Word


class AddOrUpdateWordTest(TestCase):
    """Tests add_or_update_word function"""
    def test_parameter_is_none(self):
        """Tests add_or_update_word with parameter word = None"""
        word = None
        result = add_or_update_word(word=word)
        self.assertIsNone(result)

    def test_parameter_is_empty_string(self):
        word = ""
        result = add_or_update_word(word=word)
        self.assertIsNone(result)

    def test_parameter_is_whitespace(self):
        """Tests add_or_update_word with parameter word containing only whitespace characters"""
        word = " \t"
        result = add_or_update_word(word=word)
        self.assertIsNone(result)

    def test_word_not_found_by_datamuse(self):
        """Tests add_or_update_word with a word that will not be found by datamuse"""
        word = "ssdfio"
        result = add_or_update_word(word=word)
        self.assertIsNone(result)

    @unittest.mock.patch('words.datamuse_json.query_with_retry')
    def test_connection_error(self, query_with_retryMock):
        query_with_retryMock.side_effect = ConnectionError('Datamuse service unavailable')
        message = 'Datamuse service unavailable'
        with self.assertLogs('words.datamuse_json', level='ERROR') as cm:
            result = add_or_update_word("bat")
            self.assertRegex(cm.output[0], message)
            self.assertTrue(Word.objects.filter(name="bat").exists())
            self.assertFalse(result.datamuse_success)


class AddRelatedTest(TestCase):
    def test_word_parameter_is_none(self):
        """Tests add_related with parameter word = None"""
        word = None
        code = "jja"
        message = f"Parameter 'word={word}' is None or whitespace."
        with self.assertRaisesRegex(ValueError, message):
            result = add_related(word=word, code=code)

    def test_parameter_is_empty_string(self):
        word = ""
        code = "jja"
        message = f"Parameter 'word={word}' is None or whitespace."
        with self.assertRaisesRegex(ValueError, message):
            result = add_related(word=word, code=code)

    def test_word_parameter_is_whitespace(self):
        """Tests add_related with parameter word containing only whitespace characters"""
        word = " \t"
        code = "jja"
        message = f"Parameter 'word={word}' is None or whitespace."
        with self.assertRaisesRegex(ValueError, message):
            result = add_related(word=word, code=code)

    def test_word_not_found_by_datamuse(self):
        """Tests add_related with a word that will not be found by datamuse"""
        # disabled for now: add_related no longer throws ValidationError
        # todo rewrite this whe add_related response to unrecognized words is rewritten
        pass
        # word = "ssdfio"
        # code = "jja"
        # regex = f'No related words found for word "{word}" for the chosen relations'
        # with self.assertRaisesRegex(ValidationError, regex):
        #     result = add_related(word=word, code=code)

    def test_invalid_code_parameter(self):
        word = "test"
        code = "a"
        regex = f'{code} is not a valid related word code.'
        with self.assertRaisesRegex(ValueError, regex):
            result = add_related(word=word, code=code)

    @unittest.mock.patch('words.datamuse_json.query_with_retry')
    def test_connection_error(self, query_with_retryMock):
        message = 'Datamuse service unavailable'
        query_with_retryMock.side_effect = ConnectionError(message)
        with self.assertRaisesRegex(ConnectionError, message):
            result = add_related("bat", "jja")
