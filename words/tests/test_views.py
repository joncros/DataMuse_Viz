import json
import logging
import uuid
from unittest import mock

from django import http
from fakeredis import FakeStrictRedis
from django.contrib.auth.models import User
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from rq import Queue
from rq.job import Job
from unittest import mock

from words import views
from words.datamuse_json import DatamuseWordNotRecognizedError
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

    # todo test a job_id is passed to the form

    # tests for POST

    # todo wordsetcreate mock django-rq, test rq?

    # patch so that the job always has the same id. requires an additional arg representing the mocked function be
    # passed to the test function
    @mock.patch("uuid.uuid4")
    def test_redirect(self, uuid4Mock):
        """Tests the view redirects to wordset_create_progress with appropriate arguments"""
        job_id = 'ad4dc76f-8712-4b9d-92e6-3c2e7c52e165'
        uuid4Mock.return_value = uuid.UUID(job_id)
        response = self.client.post('/words/wordset/create/', {'name': 'test1', 'words': 'word\r\ntest'})
        wordset = WordSet.objects.get(name='test1')
        self.assertRedirects(response, f'/words/wordset/create_progress/{wordset.pk}_{job_id}/')

    # patch so that the view uses a mocked Redis server and the job is executed immediately in the same thread
    @mock.patch.object(views, "rq_queue", new=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_word_occurrences_counted(self):
        """Tests that if the same word appears multiple times in the words field and/or text file, the occurrences field
         in the WordSet.words relationship is properly set."""
        from words.models import Membership

        with open("text.txt", "w") as upload_file:
            upload_file.write("pizza and pizza pizza pizza")
        with open("text.txt", "rb") as upload_file:
            response = self.client.post('/words/wordset/create/',
                                        {'name': 'test1', 'words': 'a\r\nwhat\r\nwhat\r\nand',
                                         'text_file': upload_file})

            a_member = Membership.objects.get(wordset__name='test1', word__name='a')
            self.assertEqual(a_member.occurrences, 1)

            what_member = Membership.objects.get(wordset__name='test1', word__name='what')
            self.assertEqual(what_member.occurrences, 2)

            and_member = Membership.objects.get(wordset__name='test1', word__name='and')
            self.assertEqual(and_member.occurrences, 2)

            pizza_member = Membership.objects.get(wordset__name='test1', word__name='pizza')
            self.assertEqual(pizza_member.occurrences, 4)


# patch so that jobs always have the same id. requires an additional arg representing the mocked function be passed
# to each function in the test class
@mock.patch("uuid.uuid4", return_value=uuid.UUID('ad4dc76f-8712-4b9d-92e6-3c2e7c52e165'))
class WordSetCreateProgressJSONTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.job_id = 'ad4dc76f-8712-4b9d-92e6-3c2e7c52e165'

    def test_view_url_exists_at_desired_location(self, uuid4Mock):
        """Tests that after posting to 'wordset_create', 'wordset_create_progress json' is accessible at the correct
        URL and contains a JSON response."""
        create_response = self.client.post('/words/wordset/create/', {'name': 'test1', 'words': 'word\r\ntest'})
        self.assertEqual(create_response.status_code, 302)
        json_response = self.client.get(f'/words/wordset/create_json/{self.job_id}/')
        self.assertEquals(json_response.status_code, 200)
        self.assertIsInstance(json_response, http.response.JsonResponse)

    def test_view_url_accessible_by_name_and_job_id(self, uuid4Mock):
        """Tests that after posting to 'wordset_create', 'wordset_create_progress json' is accessible by the URL name
        (with arg job_id) and contains a JSON response."""
        create_response = self.client.post('/words/wordset/create/', {'name': 'test1', 'words': 'word\r\ntest'})
        self.assertEqual(create_response.status_code, 302)
        json_response = self.client.get(reverse("wordset_create_progress json", args=[self.job_id]))
        self.assertEquals(json_response.status_code, 200)
        self.assertIsInstance(json_response, http.response.JsonResponse)

    @mock.patch.object(views, "rq_queue", new=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_job_progress_included_in_json(self, uuid4Mock):
        """Tests that after posting to 'wordset_create', the response at 'wordset_create_progress json' contains
        attributes indicating the state of the job."""
        # mocked Redis server
        conn = FakeStrictRedis()

        # replace redis connection with conn, replace the queue used by the view with a queue that uses conn
        # and immediately runs the task in the current thread
        with mock.patch.object(views, "rq_queue", new=Queue(is_async=False, connection=conn)):
            with mock.patch.object(views, "redis_cursor", new=conn):
                self.client.post('/words/wordset/create/', {'name': 'test1', 'words': 'word\r\ntest'})
                job = Job.fetch(self.job_id, connection=conn)
                logger.info(f'job {job}, connection {job.connection}')
                logger.info(f'status {job.get_status()}, meta {job.meta}')
                response = self.client.get(reverse("wordset_create_progress json", args=[self.job_id]))
                content = json.loads(response.content)
                self.assertIn('status', content)
                self.assertIn('potential_words', content)
                self.assertIn('processed_words', content)
                self.assertIn('recognized_words', content)


# patch so that jobs always have the same id. requires an additional arg representing the mocked function be passed
# to each function in the test class
# patch so that the view uses a mocked Redis server and the job is executed immediately in the same thread
@mock.patch("uuid.uuid4", return_value=uuid.UUID('ad4dc76f-8712-4b9d-92e6-3c2e7c52e165'))
@mock.patch.object(views, "rq_queue", new=Queue(is_async=False, connection=FakeStrictRedis()))
class WordSetCreateProgressTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.job_id = 'ad4dc76f-8712-4b9d-92e6-3c2e7c52e165'

    def test_view_url_exists_at_desired_location(self, uuid4Mock):
        """Tests that after posting to 'wordset_create', 'wordset_create_progress' is accessible at the correct URL"""
        create_response = self.client.post('/words/wordset/create/', {'name': 'test1', 'words': 'word\r\ntest'})
        wordset = WordSet.objects.get(name="test1")
        progress_response = self.client.post(f'/words/wordset/create_progress/{wordset.pk}_{self.job_id}/')
        self.assertEqual(progress_response.status_code, 200)

    def test_view_url_accessible_by_name(self, uuid4Mock):
        """Tests that after posting to 'wordset_create', 'wordset_create_progress' is accessible by the URL name."""
        create_response = self.client.post('/words/wordset/create/', {'name': 'test1', 'words': 'word\r\ntest'})
        wordset = WordSet.objects.get(name="test1")
        progress_response = self.client.get(reverse("wordset_create_progress", args=[wordset.pk, self.job_id]))
        self.assertEqual(progress_response.status_code, 200)


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

    def test_wordset_context_includes_words_missing_data(self):
        """Tests that the context includes a QuerySet of the words in the WordSet for which datamuse_success is False"""
        wordset = WordSet.objects.get(name="test1")
        wordset.words.add(
            Word.objects.create(name="web", datamuse_success=False),
            Word.objects.create(name="site", datamuse_success=False)
        )
        response = self.client.get(wordset.get_absolute_url())
        self.assertIn('words_missing_data', response.context)
        words_missing_data = response.context['words_missing_data']
        self.assertTrue(words_missing_data.filter(name="web").exists())
        self.assertTrue(words_missing_data.filter(name="site").exists())


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


class VisualizationRelatedWordsTest(TestCase):
    """Tests visualization_related_words view."""

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/words/related_words/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('viz related words'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('viz related words'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'words/visualization_related_words.html')

    def test_navbar_context_item(self):
        """Tests that an item exists in view context that sets the page to active in the navbar"""
        response = self.client.get(reverse('viz related words'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['navbar_related_words'], 'active')

    def test_visualization_title_test(self):
        """Tests that the correct visualization title is passed in the context"""
        response = self.client.get(reverse('viz related words'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['viz_title'], 'Related Words')

    @mock.patch('words.datamuse_json.query_with_retry')
    def test_datamuse_connection_error(self, query_with_retryMock):
        """Tests that a message is included in the context if the Datamuse call results in a ConnectionError"""
        post_dict = {'word': 'walk', 'relations': ['jja']}
        message = 'Datamuse service unavailable'
        query_with_retryMock.side_effect = ConnectionError(message)
        with self.assertRaises(ConnectionError):
            response = self.client.post(reverse('viz related words'), post_dict)
            self.assertEqual(response.status_code, 200)
            self.assertIn('datamuse_error', response.context)
            self.assertIn(message, response.context['datamuse_error'])

    @mock.patch('words.datamuse_json.add_related')
    def test_datamuse_json_value_error(self, add_relatedMock):
        """Tests that a message is included in the context if the Datamuse call results in a ValueError"""
        post_dict = {'word': 'walk', 'relations': ['jja']}
        message = 'ValueError message'
        add_relatedMock.side_effect = ValueError(message)
        with self.assertRaises(ValueError):
            response = self.client.post(reverse('viz related words'), post_dict)
            self.assertEqual(response.status_code, 200)
            self.assertIn('datamuse_error', response.context)
            self.assertIn(message, response.context['datamuse_error'])

    @mock.patch('words.datamuse_json.add_related')
    def test_datamuse_word_not_recognized(self, add_relatedMock):
        """Tests that a message is included in the context if a word is submitted that Datamuse will not recognize."""
        word = 'ffpq'
        post_dict = {'word': word, 'relations': ['jja']}
        add_relatedMock.side_effect = DatamuseWordNotRecognizedError(word)
        message = f'word "{word}" was not recognized by Datamuse'
        # with self.assertRaises(DatamuseWordNotRecognizedError):
        response = self.client.post(reverse('viz related words'), post_dict)
        self.assertEqual(response.status_code, 200)
        self.assertIn('datamuse_error', response.context)
        self.assertIn(message, response.context['datamuse_error'])

    @mock.patch('words.datamuse_json.add_related')
    def test_datamuse_query_result_none(self, add_relatedMock):
        """Tests that a message is included in the context when the word is valid, but no related words are returned"""
        word = 'walk'
        word_instance = Word.objects.get_or_create(name="walk")[0]
        post_dict = {'word': word, 'relations': ['jja']}
        add_relatedMock.return_value = (
            word_instance,
            word_instance.jja.none()        # an empty set of words
        )
        message = f'No related words found for word "{word}" for the chosen relations'
        response = self.client.post(reverse('viz related words'), post_dict)
        self.assertEqual(response.status_code, 200)
        self.assertIn('datamuse_error', response.context)
        self.assertIn(message, response.context['datamuse_error'])

    @mock.patch('words.datamuse_json.add_related')
    def test_datamuse_some_relations_return_empty_results(self, add_relatedMock):
        """Tests that a relation code is omitted from the result dict if there are no results for that relation."""
        word = 'walk'
        codes = ['jja', 'jjb']
        jja_verbose = Word._meta.get_field('jja').verbose_name
        jjb_verbose = Word._meta.get_field('jjb').verbose_name

        word_instance = Word.objects.get_or_create(name=word)[0]
        jja_word = Word.objects.get_or_create(name="hike")[0]
        word_instance.jja.add(jja_word, through_defaults={'score': 100})
        word_instance.save()

        # verify that for the test database, item count of word_instance.jjb is 0
        self.assertEqual(word_instance.jjb.count(), 0)

        # return mocked values from add_related
        values = {'jja': (word_instance, word_instance.jja_relations),
                  'jjb': (word_instance, word_instance.jjb_relations)}

        def side_effect(*args):
            return values[args[1]]

        add_relatedMock.side_effect = side_effect

        post_dict = {'word': word, 'relations': codes}
        response = self.client.post(reverse('viz related words'), post_dict)
        self.assertEqual(response.status_code, 200)

        # find which relations were included in result_dict
        result_dict_children = response.context['json_object']['children']
        included_relations = []
        for child in result_dict_children:
            included_relations.append(child['name'])

        self.assertIn(jja_verbose, included_relations)
        self.assertNotIn(jjb_verbose, included_relations)

    @mock.patch('words.datamuse_json.add_related')
    def test_relations_with_no_results_added_to_context_item(self, add_relatedMock):
        """Tests that relations for which there were no results are added to context['relations_with_no_results']"""
        word = 'walk'
        codes = ['jja', 'jjb']
        jja_verbose = Word._meta.get_field('jja').verbose_name
        jjb_verbose = Word._meta.get_field('jjb').verbose_name

        word_instance = Word.objects.get_or_create(name=word)[0]
        jja_word = Word.objects.get_or_create(name="hike")[0]
        word_instance.jja.add(jja_word, through_defaults={'score': 100})
        word_instance.save()

        # verify that for the test database, item count of word_instance.jjb is 0
        self.assertEqual(word_instance.jjb.count(), 0)

        # return mocked values from add_related
        values = {'jja': (word_instance, word_instance.jja_relations), 'jjb': (word_instance, word_instance.jjb_relations)}

        def side_effect(*args):
            return values[args[1]]

        add_relatedMock.side_effect = side_effect

        post_dict = {'word': word, 'relations': codes}
        response = self.client.post(reverse('viz related words'), post_dict)
        self.assertEqual(response.status_code, 200)
        self.assertIn('relations_with_no_results', response.context)
        self.assertNotIn(jja_verbose, response.context['relations_with_no_results'])
        self.assertIn(jjb_verbose, response.context['relations_with_no_results'])


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

    def test_id_parsed_from_url(self):
        """Tests that if id is included in the url query string, the initial value of 'word_set' in the form is set to
        the corresponding WordSet."""
        wordset = WordSet.objects.create(name="test")
        response = self.client.get(f'/words/frequencies/?id={wordset.id}')
        self.assertEqual(response.context['form'].initial['word_set'], wordset)

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


class VisualizationFrequencyScatterplotTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/words/scatterplot/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('viz frequency scatterplot'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('viz frequency scatterplot'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'words/visualization_frequency_scatterplot.html')

    def test_navbar_context_item(self):
        """Tests that an item exists in view context that sets the page to active in the navbar"""
        response = self.client.get(reverse('viz frequency scatterplot'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['navbar_frequency_scatterplot'], 'active')

    def test_visualization_title_test(self):
        """Tests that the correct visualization title is passed in the context"""
        response = self.client.get(reverse('viz frequency scatterplot'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['viz_title'], 'Occurrences vs Frequencies Scatterplot')

    def test_id_parsed_from_url(self):
        """Tests that if id is included in the url query string, the initial value of 'word_set' in the form is set to
        the corresponding WordSet."""
        wordset = WordSet.objects.create(name="test")
        response = self.client.get(f'/words/scatterplot/?id={wordset.id}')
        self.assertEqual(response.context['form'].initial['word_set'], wordset)
