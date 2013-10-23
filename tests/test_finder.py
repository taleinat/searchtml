"""Tests for `searchtml.finder` module."""
from tests.compat import unittest

from searchtml.finder import ElementFinder
from searchtml.matchers import TagElementMatcher, ElementMatcher
import xml.etree.ElementTree as ElementTree
import lxml.html


class TestFinder(unittest.TestCase):
    def test_single_tag_matcher(self):
        tree = ElementTree.fromstring('''\
            <html>
                <body>
                    <h1>str1</h1>
                    <h2>str2</h2>
                    <h3>str3</h3>
                </body>
            </html>
        ''')

        finder = ElementFinder()
        tag_matcher = TagElementMatcher(tags=['h1', 'h3'])
        finder.add_element_matcher(tag_matcher)
        results = finder.findElements(tree)

        # check that the keys of the results dict are the supplied matchers
        self.assertEquals(results.keys(), [tag_matcher])

        # check that two tags were matched by the tag_matcher
        self.assertEquals(2, len(results[tag_matcher]))

        # check matching of the h1 node
        h1_node = results[tag_matcher][0]
        self.assertEquals(h1_node.tag, 'h1')
        self.assertEquals(h1_node.text, 'str1')

        # check matching of the h3 node
        h3_node = results[tag_matcher][1]
        self.assertEquals(h3_node.tag, 'h3')
        self.assertEquals(h3_node.text, 'str3')

    def test_lxml_ignore_comments(self):
        tree = lxml.html.document_fromstring('''\
            <html>
                <body>
                    <!--
                    <h1>str1</h1>
                    -->
                </body>
            </html>
        ''')

        finder = ElementFinder()
        tag_matcher = TagElementMatcher(tags=['h1'])
        finder.add_element_matcher(tag_matcher)
        results = finder.findElements(tree)

        # check that no tags were matched by the tag_matcher
        self.assertEquals(0, len(results[tag_matcher]))

    def test_skip_tags_matched_by_ignore_matcher(self):
        tree = ElementTree.fromstring('''\
            <html>
                <body>
                    <div>
                        <h1>str1</h1>
                    </div>
                </body>
            </html>
        ''')

        finder = ElementFinder()
        tag_matcher = TagElementMatcher(tags=['h1'])
        finder.add_element_matcher(tag_matcher)
        finder.add_ignore_element_matcher(TagElementMatcher(tags=['div']))
        results = finder.findElements(tree)

        # check that no tags were matched by the tag_matcher
        self.assertEquals(0, len(results[tag_matcher]))

    def test_single_non_tag_matcher(self):
        tree = ElementTree.fromstring('''\
            <html>
                <body>
                    <h1>str1</h1>
                    <h1>str2</h1>
                </body>
            </html>
        ''')

        class Matcher(ElementMatcher):
            def doesMatch(self, element):
                return 'str1' in element.text

        finder = ElementFinder()
        tag_matcher = Matcher()
        finder.add_element_matcher(tag_matcher)
        results = finder.findElements(tree)

        # check that only the first element was matched by the tag_matcher
        self.assertEquals(1, len(results[tag_matcher]))
        self.assertEquals('str1', results[tag_matcher][0].text)

    def test_skip_tags_matched_by_non_tag_ignore_matcher(self):
        tree = ElementTree.fromstring('''\
            <html>
                <body>
                    <h1 skip="yes">str1</h1>
                </body>
            </html>
        ''')

        class Matcher(ElementMatcher):
            def doesMatch(self, element):
                return element.get('skip') == 'yes'

        finder = ElementFinder()
        matcher = TagElementMatcher(tags=['h1'])
        finder.add_element_matcher(matcher)
        ignore_matcher = Matcher()
        finder.add_ignore_element_matcher(ignore_matcher)
        results = finder.findElements(tree)

        # check that no tags were matched by the tag_matcher
        self.assertEquals(0, len(results[matcher]))
