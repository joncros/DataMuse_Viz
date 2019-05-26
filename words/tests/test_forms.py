from django import forms
from django.test import TestCase

from words.forms import WordForm, WordSetCreateForm, WordCharField


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
        text = "Type the words to include in the set (one word or phrase per line)"
        self.assertEqual(text, form.fields['words'].help_text)

    def test_words_field(self):
        """Test that the words field is of the correct class and strip attribute is false"""
        form = WordSetCreateForm()
        field = form.fields['words']
        self.assertIsInstance(field, WordCharField)
        self.assertFalse(field.strip)


class WordFormTest(TestCase):
    def test_correct_fields_present(self):
        form = WordForm()
        self.assertIn('name', form.fields)
        self.assertIn('language', form.fields)
        self.assertIn('relation', form.fields)
        self.assertIn('word_set', form.fields)

    def test_word_name_field_label(self):
        """The label for the word name should be 'word'."""
        form = WordForm()
        self.assertTrue(form.fields['name'].label == 'Word')


# todo? test password reset form? (I may want to add a label for the email field)
