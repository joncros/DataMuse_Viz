from django.test import TestCase, SimpleTestCase
from django.urls import reverse


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
        self.assertTrue(response.context['navbar_index'] == 'active')


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
        self.assertTrue(response.context['navbar_relation_viz'] == 'active')

    def test_visualization_title_test(self):
        """Tests that the correct visualization title is passed in the context"""
        response = self.client.get(reverse('relations viz'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['viz_title'] == 'Word Relationships')


    # todo test viz description included in context
