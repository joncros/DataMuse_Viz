import logging

from django.contrib.auth.models import User
from django.test import TestCase, SimpleTestCase
from django.urls import reverse

from words.models import WordSet, Word

logger = logging.getLogger(__name__)


class IndexTest(SimpleTestCase):
    """Tests 'index' view."""

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/words/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'words/index.html')

    def test_base_url_redirects_to_correct_url(self):
        """Test that empty path '/' redirects to 'words/index'"""
        response = self.client.get('')
        self.assertRedirects(response, '/words/', status_code=301)  # 301 response indicates permanent redirection

    def test_navbar_context_item(self):
        """Tests that an item exists in view context that sets the page to active in the navbar"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['navbar_index'], 'active')


class WordSetCreateTest(TestCase):
    """Tests 'wordset_create' view"""

    # tests for GET

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/words/wordset/create/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('wordset_create'))
        self.assertEqual(response.status_code, 200)

    def test_navbar_context_item(self):
        """Tests that an item exists in view context that sets the page to active in the navbar"""
        response = self.client.get(reverse('wordset_create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['navbar_wordset_create'], 'active')

    def test_if_user_not_authenticated_creator_field_blank_(self):
        """Tests that if user is not logged in, the value of the creator field is blank"""
        response = self.client.get(reverse('wordset_create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['creator'].value(), '')

    def test_if_user_authenticated_creator_field_value_is_user_(self):
        """Tests that if user is not logged in, the value of the creator field is blank"""
        test_user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK')
        login = self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('wordset_create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['creator'].value(), test_user.id)

    # tests for POST

    def test_redirect(self):
        response = self.client.post('/words/wordset/create/', {'name': 'test1', 'words': 'word\r\ntest'})
        wordset = WordSet.objects.get(name='test1')
        self.assertRedirects(response, f'/words/wordset/{wordset.pk}')

    def test_redirect_if_next_in_request(self):
        response = self.client.post('/words/wordset/create/?next=/words/', {'name': 'test1', 'words': 'word\r\ntest'})
        self.assertRedirects(response, '/words/')


class WordSetDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        test_user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK')
        WordSet.objects.create(name="test1", creator=test_user)
        WordSet.objects.create(name="test2")

    def test_view_url_exists_at_desired_location(self):
        wordset = WordSet.objects.get(name='test1')
        response = self.client.get(f'/words/wordset/{wordset.pk}')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_object_get_absolute_url(self):
        wordset = WordSet.objects.get(name='test1')
        response = self.client.get(wordset.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name_and_primary_key(self):
        wordset = WordSet.objects.get(name='test1')
        response = self.client.get(reverse('wordset-detail', args=[wordset.pk]))
        self.assertEqual(response.status_code, 200)

    def test_if_wordset_creator_none_delete_link_not_present(self):
        wordset = WordSet.objects.get(name="test2")
        response = self.client.get(reverse('wordset-detail', args=[wordset.pk]))
        self.assertNotContains(response, f'<a href="/words/wordset/{wordset.pk}/delete/">Delete Word Set</a>',
                               html=True)

    def test_if_wordset_creator_not_logged_in_delete_link_not_present(self):
        """Login a user other than the word set creator and assert delete link not present"""
        wordset = WordSet.objects.get(name="test1")
        test_user = User.objects.create_user(username='testuser2', password='qq<ISRUkw+tuK')
        login = self.client.login(username='testuser2', password='qq<ISRUkw+tuK')
        response = self.client.get(reverse('wordset-detail', args=[wordset.pk]))
        self.assertNotContains(response, f'<a href="/words/wordset/{wordset.pk}/delete/">Delete Word Set</a>',
                               html=True)

    def test_if_wordset_creator_logged_in_delete_link_present(self):
        wordset = WordSet.objects.get(name="test1")
        self.client.login(username='testuser', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('wordset-detail', args=[wordset.pk]))
        self.assertContains(response, f'<a href="/words/wordset/{wordset.pk}/delete/">Delete Word Set</a>', html=True)


class WordSetDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='ISRUkw+tuK1X<')
        WordSet.objects.create(name="test1", creator=test_user1)
        WordSet.objects.create(name="test2")

    def test_view_url_exists_at_desired_location(self):
        wordset = WordSet.objects.get(name='test1')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(f'/words/wordset/{wordset.pk}/delete/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name_and_primary_key(self):
        wordset = WordSet.objects.get(name='test1')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('wordset_delete', args=[wordset.pk]))
        self.assertEqual(response.status_code, 200)

    def test_403_if_wrong_user_logged_in(self):
        wordset = WordSet.objects.get(name='test1')
        login = self.client.login(username='testuser2', password='ISRUkw+tuK1X<')
        response = self.client.get(reverse('wordset_delete', args=[wordset.pk]))
        self.assertEqual(response.status_code, 403)

    def test_redirect_if_user_not_logged_in(self):
        wordset = WordSet.objects.get(name='test1')
        response = self.client.get(reverse('wordset_delete', args=[wordset.pk]))
        self.assertEqual(response.status_code, 302)

    def test_403_if_user_not_logged_in_wordset_creator_none(self):
        wordset = WordSet.objects.get(name='test2')
        response = self.client.get(reverse('wordset_delete', args=[wordset.pk]))
        self.assertEqual(response.status_code, 403)

    def test_403_if_user_logged_in_wordset_creator_none(self):
        wordset = WordSet.objects.get(name='test2')
        login = self.client.login(username='testuser2', password='ISRUkw+tuK1X<')
        response = self.client.get(reverse('wordset_delete', args=[wordset.pk]))
        self.assertEqual(response.status_code, 403)


class WordSetListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/words/wordsets/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('wordsets'))
        self.assertEqual(response.status_code, 200)

    def test_navbar_context_item(self):
        """Tests that an item exists in view context that sets the page to active in the navbar"""
        response = self.client.get(reverse('wordsets'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['navbar_wordsets'], 'active')


class GetRelationVizTest(TestCase):
    """Tests get_relation_viz view."""

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/words/relations/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('relations viz'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('relations viz'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'words/word_relationships.html')

    def test_navbar_context_item(self):
        """Tests that an item exists in view context that sets the page to active in the navbar"""
        response = self.client.get(reverse('relations viz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['navbar_relation_viz'], 'active')

    def test_visualization_title_test(self):
        """Tests that the correct visualization title is passed in the context"""
        response = self.client.get(reverse('relations viz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['viz_title'], 'Word Relationships')


class VisualizationFrequencyTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/words/frequencies/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('viz frequency'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('viz frequency'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'words/visualization_frequency.html')

    def test_navbar_context_item(self):
        """Tests that an item exists in view context that sets the page to active in the navbar"""
        response = self.client.get(reverse('viz frequency'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['navbar_visualization_frequency'], 'active')

    def test_visualization_title_test(self):
        """Tests that the correct visualization title is passed in the context"""
        response = self.client.get(reverse('viz frequency'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['viz_title'], 'Word Frequencies')

    # tests for POST

    def test_wordset_data_in_post(self):
        """Tests when POST used with a WordSet, context contains 'wordset_data', json formatted for the bubble chart"""
        # create a WordSet to use
        word_set = WordSet.objects.create(name='test')
        word_set.words.add(Word.objects.create(name="and")),
        word_set.words.add(Word.objects.create(name="for"))
        word_set.words.add(Word.objects.create(name="bike"))
        postData = {'word_set': word_set.id}
        response = self.client.post('/words/frequencies/', data=postData)
        data_item_pattern = "{" \
                            "'name': '\\s*'," \
                            "'title': '\\s*'," \
                            "'group': 'test'," \
                            "'value': \\d*\\.\\d*" \
                            "}"
        pattern = "[" + data_item_pattern + "," + data_item_pattern + "," + data_item_pattern + "]"
        wordset_data = response.context['wordset_data']
        self.assertRegex(wordset_data, pattern)

    # todo test viz description included in context
