from django.test import TestCase

from words.forms import WordForm


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