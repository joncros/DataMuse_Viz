import unittest.mock

from django.test import TestCase

from words.datamuse_json import add_or_update_word, add_related


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
        query_with_retryMock.side_effect = ConnectionError('DataMuse service unavailable')
        message = 'DataMuse service unavailable'
        with self.assertLogs('words.datamuse_json', level='ERROR') as cm:
            result = add_or_update_word("bat")
            self.assertRegex(cm.output[0], message)
            self.assertIsNone(result)


class AddRelatedTest(TestCase):
    def test_word_parameter_is_none(self):
        """Tests add_related with parameter word = None"""
        pass

    def test_parameter_is_empty_string(self):
        pass

    def test_word_parameter_is_whitespace(self):
        """Tests add_related with parameter word containing only whitespace characters"""
        pass

    def test_word_not_found_by_datamuse(self):
        """Tests add_related with a word that will not be found by datamuse"""

    def test_invalid_code_parameter(self):
        pass

    def test_connection_error(self):
        pass
