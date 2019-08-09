import os
from string import punctuation
from unittest import mock

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from django.test import TestCase

from words.forms import RelatedWordsForm, WordSetCreateForm, WordCharField, WordFileField, WordSetChoice, \
    ScatterplotWordSetChoice
from words.models import WordSet, Word


class WordSetCreateFormTest(TestCase):
    def test_correct_fields_present(self):
        form = WordSetCreateForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('creator', form.fields)
        self.assertIn('words', form.fields)

    def test_creator_field_hidden(self):
        form = WordSetCreateForm()
        self.assertIsInstance(form.fields['creator'].widget, forms.widgets.HiddenInput)

    def test_words_field_help_text(self):
        form = WordSetCreateForm()
        text = "(Optional) Type the words to include in the set (one word or phrase per line)"
        self.assertEqual(text, form.fields['words'].help_text)

    def test_words_field(self):
        """Test that the words field is of the correct class and strip attribute is false"""
        form = WordSetCreateForm()
        field = form.fields['words']
        self.assertIsInstance(field, WordCharField)
        self.assertFalse(field.strip)

    def test_text_file_field(self):
        """Tests that the field text_file is of the correct class and is not required."""
        form = WordSetCreateForm()
        field = form.fields['text_file']
        self.assertIsInstance(field, WordFileField)
        self.assertFalse(field.required)

    def test_text_file_field_help_text(self):
        form = WordSetCreateForm()
        field = form.fields['text_file']
        text = "(Optional) Upload a text file containing words (multiple words per line) " \
               "to include in the set. The text is split into individual words (no " \
               "phrases will be detected). Punctuation (apart from hyphens) will be ignored."
        self.assertEqual(field.help_text, text)

    def test_text_file_upload(self):
        with open("text.txt", "w") as upload_file:
            upload_file.write("Some text")
        with open("text.txt", "rb") as upload_file:
            post_dict = {'name': 'test'}
            file_dict = {'text_file': InMemoryUploadedFile(
                upload_file, 'text_file', upload_file.name, '', os.path.getsize('text.txt'), None)}
            form = WordSetCreateForm(post_dict, file_dict)
            self.assertTrue(form.is_valid())

    def test_text_file_size_limit(self):
        """Tests that a ValidationError is thrown by text_file field if the file is greater than 10mb"""
        size = 10000001
        with open("text.txt", "w") as upload_file:
            upload_file.truncate(size)
        with open("text.txt", "rb") as upload_file:
            post_dict = {'name': 'test'}
            file_dict = {'text_file': InMemoryUploadedFile(
                upload_file, 'text_file', upload_file.name, '', os.path.getsize('text.txt'), None)}
            form = WordSetCreateForm(post_dict, file_dict)
            message = "Uploaded file is to large; file size cannot exceed 10 mb."
            self.assertFalse(form.is_valid())
            self.assertIn(message, form.errors['text_file'])

    def test_text_file_wrong_file_type(self):
        """Tests that a ValidationError is thrown by text_file field when the file is not text/plain"""
        upload_file = open('manage.py', 'rb')
        post_dict = {'name': 'test'}
        file_dict = {'text_file': InMemoryUploadedFile(
            upload_file, 'text_file', upload_file.name, '', os.path.getsize('manage.py'), None)}
        message = "Uploaded file is not a plain text file."
        form = WordSetCreateForm(post_dict, file_dict)
        self.assertFalse(form.is_valid())
        self.assertIn(message, form.errors['text_file'])

    def test_text_file_punctuation_next_to_words_stripped(self):
        """Test for an uploaded text file to confirm punctuation at the beginning or end of each word is stripped."""
        with open("text.txt", "w") as upload_file:
            upload_file.write("?Some text\" !and some" + punctuation + " punctuation.")
        with open("text.txt", "rb") as upload_file:
            post_dict = {'name': 'test'}
            file_dict = {'text_file': InMemoryUploadedFile(
                upload_file, 'text_file', upload_file.name, '', os.path.getsize('text.txt'), None)}
            form = WordSetCreateForm(post_dict, file_dict)
            self.assertTrue(form.is_valid())
            expected = ['Some', 'text', 'and', 'some', 'punctuation']
            self.assertListEqual(form.cleaned_data['text_file'], expected)

    def test_text_file_em_dash_stripped(self):
        """Tests that the em dash, '--' in plain text, is removed from the text of an uploaded file."""
        with open("text.txt", "w") as upload_file:
            upload_file.write(f"--Some text--with-- -- em -- dashes--")
        with open("text.txt", "rb") as upload_file:
            post_dict = {'name': 'test'}
            file_dict = {'text_file': InMemoryUploadedFile(
                upload_file, 'text_file', upload_file.name, '', os.path.getsize('text.txt'), None)}
            form = WordSetCreateForm(post_dict, file_dict)
            self.assertTrue(form.is_valid())
            expected = ['Some', 'text', 'with', 'em', 'dashes']
            self.assertListEqual(form.cleaned_data['text_file'], expected)

    def test_text_file_all_puncuation_except_hyphens_stripped_from_words(self):
        """Tests that, except for the hyphen '-', punctuation is stripped from the middle of words in uploaded text."""
        with open("text.txt", "w") as upload_file:
            # string.punctuation[12] is the hyphen character
            upload_file.write(
                f"Some text" + punctuation[:12] + "with punctuation" + punctuation[13:] + "and a hyphenated-word")
        with open("text.txt", "rb") as upload_file:
            post_dict = {'name': 'test'}
            file_dict = {'text_file': InMemoryUploadedFile(
                upload_file, 'text_file', upload_file.name, '', os.path.getsize('text.txt'), None)}
            form = WordSetCreateForm(post_dict, file_dict)
            self.assertTrue(form.is_valid())
            expected = ['Some', 'text', 'with', 'punctuation', 'and', 'a', 'hyphenated-word']
            self.assertListEqual(form.cleaned_data['text_file'], expected)


class RelatedWordsFormTest(TestCase):
    def test_correct_fields_present(self):
        form = RelatedWordsForm()
        self.assertIn('word', form.fields)
        self.assertIn('relations', form.fields)
        self.assertIn('results', form.fields)

    def test_results_field_hidden_and_not_required(self):
        form = RelatedWordsForm()
        self.assertIsInstance(form.fields['results'].widget, forms.widgets.HiddenInput)
        self.assertFalse(form.fields['results'].required)

    def test_relations_field_nothing_selected(self):
        post_dict = {'word': 'walk'}
        message = 'Please check at least one relation.'
        form = RelatedWordsForm(post_dict)
        self.assertFalse(form.is_valid())
        self.assertIn(message, form.non_field_errors())

    @mock.patch('words.datamuse_json.query_with_retry')
    def test_datamuse_connection_error(self, query_with_retryMock):
        """Tests that a ConnectionError from datamuse_json results in a ValidationError"""
        post_dict = {'word': 'walk', 'relations': ['jja']}
        message = 'Datamuse service unavailable'
        query_with_retryMock.side_effect = ConnectionError(message)
        form = RelatedWordsForm(post_dict)
        self.assertFalse(form.is_valid())
        self.assertIn(message, form.non_field_errors())

    @mock.patch('words.datamuse_json.add_related')
    def test_datamuse_json_value_error(self, add_relatedMock):
        """Tests that a ValueError from datamuse_json results in a ValidationError"""
        post_dict = {'word': 'walk', 'relations': ['jja']}
        message = 'ValueError message'
        add_relatedMock.side_effect = ValueError(message)
        form = RelatedWordsForm(post_dict)
        self.assertFalse(form.is_valid())
        self.assertIn("Invalid parameter for Datamuse query: " + message, form.non_field_errors())

    @mock.patch('words.datamuse_json.add_related')
    def test_datamuse_query_result_none(self, add_relatedMock):
        """Tests there is a non-field error when no related words are returned by Datamuse"""
        word = 'walk'
        word_instance = Word.objects.get_or_create(name="walk")[0]
        post_dict = {'word': word, 'relations': ['jja']}
        add_relatedMock.return_value = (
            word_instance,
            word_instance.jja.none()        # an empty set of words
        )
        message = f'No related words found for word "{word}" for the chosen relations'
        form = RelatedWordsForm(post_dict)
        self.assertFalse(form.is_valid())
        self.assertIn(message, form.non_field_errors())

    @mock.patch('words.datamuse_json.add_related')
    def test_datamuse_some_relations_return_empty_results(self, add_relatedMock):
        """Tests that a relation code is omitted from the result dict if there are no results for that relation."""
        word = 'walk'
        codes = ['jja', 'jjb']
        word_instance = Word.objects.get_or_create(name=word)[0]
        jja_word = Word.objects.get_or_create(name="hike")[0]
        word_instance.jja.add(jja_word)
        word_instance.save()
        values = {'jja': (word_instance, word_instance.jja), 'jjb': (word_instance, word_instance.jjb)}

        def side_effect(*args):
            return values[args[1]]

        add_relatedMock.side_effect = side_effect

        post_dict = {'word': word, 'relations': codes}
        form = RelatedWordsForm(post_dict)
        self.assertTrue(form.is_valid())
        self.assertIn('jja', form.cleaned_data['results'])
        self.assertNotIn('jjb', form.cleaned_data['results'])


class WordSetChoiceTest(TestCase):
    def test_correct_fields_present(self):
        form = WordSetChoice()
        self.assertIn('word_set', form.fields)
        self.assertIn('frequency_gt', form.fields)
        self.assertIn('frequency_lt', form.fields)

    def test_frequency_gt_and_frequency_lt_fields_optional(self):
        form = WordSetChoice()
        self.assertFalse(form.fields['frequency_gt'].required)
        self.assertFalse(form.fields['frequency_lt'].required)

    def test_field_labels(self):
        form = WordSetChoice()
        gt_label = "Only show words with frequency greater than"
        lt_label = "Only show words with frequency less than"
        self.assertEqual(form.fields['frequency_gt'].label, gt_label)
        self.assertEqual(form.fields['frequency_lt'].label, lt_label)

    def test_invalid_if_frequency_gt_greater_than_frequency_lt(self):
        gt_value = 1000
        lt_value = 20
        word_set = WordSet.objects.create(name='test')
        message = "frequency less than field must be greater than frequency greater than field"
        post_dict = {'word_set': word_set, 'frequency_gt': gt_value, 'frequency_lt': lt_value}
        form = WordSetChoice(post_dict)
        self.assertFalse(form.is_valid())
        self.assertIn(message, form.errors['__all__'])


class ScatterplotWordSetChoiceTest(TestCase):
    def test_correct_fields_present(self):
        form = ScatterplotWordSetChoice()
        self.assertIn('word_set', form.fields)
        self.assertIn('frequency_gt', form.fields)
        self.assertIn('frequency_lt', form.fields)
        self.assertIn('occurrences_gt', form.fields)
        self.assertIn('occurrences_lt', form.fields)

    def test_gt_and_lt_fields_optional(self):
        form = ScatterplotWordSetChoice()
        self.assertFalse(form.fields['frequency_gt'].required)
        self.assertFalse(form.fields['frequency_lt'].required)
        self.assertFalse(form.fields['occurrences_gt'].required)
        self.assertFalse(form.fields['occurrences_lt'].required)

    def test_field_labels(self):
        form = ScatterplotWordSetChoice()
        frequency_gt_label = "Only show words with frequency greater than"
        frequency_lt_label = "Only show words with frequency less than"
        occurrences_gt_label = "Only show words with occurrences greater than"
        occurrences_lt_label = "Only show words with occurrences less than"
        self.assertEqual(form.fields['frequency_gt'].label, frequency_gt_label)
        self.assertEqual(form.fields['frequency_lt'].label, frequency_lt_label)
        self.assertEqual(form.fields['occurrences_gt'].label, occurrences_gt_label)
        self.assertEqual(form.fields['occurrences_lt'].label, occurrences_lt_label)

    def test_invalid_if_frequency_gt_greater_than_frequency_lt(self):
        gt_value = 1000
        lt_value = 20
        word_set = WordSet.objects.create(name='test1')
        message = "frequency less than field must be greater than frequency greater than field"
        post_dict = {'word_set': word_set, 'frequency_gt': gt_value, 'frequency_lt': lt_value}
        form = ScatterplotWordSetChoice(post_dict)
        self.assertFalse(form.is_valid())
        self.assertIn(message, form.errors['__all__'])

    def test_invalid_if_occurrences_gt_greater_than_occurrences_lt(self):
        gt_value = 10
        lt_value = 2
        word_set = WordSet.objects.create(name='test2')
        message = "occurrences less than field must be greater than occurrences greater than field"
        post_dict = {'word_set': word_set, 'occurrences_gt': gt_value, 'occurrences_lt': lt_value}
        form = ScatterplotWordSetChoice(post_dict)
        self.assertFalse(form.is_valid())
        self.assertIn(message, form.errors['__all__'])
