"""Tests for `searchtml.matchers` module."""
from searchtml.matchers import NoAttributesTagElementMatcher
from tests.compat import unittest

from xml.etree.ElementTree import Element

from searchtml.matchers import ElementMatcher, TagElementMatcher,\
    AttributeSubstringTagElementMatcher


class TestAbstractBaseClass(unittest.TestCase):
    def test_doesMatch_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            ElementMatcher().doesMatch(Element('a'))


class TestTagElementMatcher(unittest.TestCase):
    def test_string_parameter_exception(self):
        self.assertRaises(TypeError, lambda: TagElementMatcher('a string'))

    def test_basic_match(self):
        element = Element('a')
        self.assertTrue(TagElementMatcher(['a']).doesMatch(element))
        self.assertTrue(TagElementMatcher(['a', 'b']).doesMatch(element))
        self.assertFalse(TagElementMatcher(['b']).doesMatch(element))

    def test_case_insensitive_match(self):
        element = Element('a')
        self.assertTrue(TagElementMatcher(['a']).doesMatch(element))


class TestNoAttributesTagElementMatcher(unittest.TestCase):
    def test_matches_no_attrs(self):
        element = Element('a')
        matcher = NoAttributesTagElementMatcher(['a'])
        self.assertTrue(matcher.doesMatch(element))

    def test_doesnt_match_with_attrs(self):
        element = Element('a', href='web address')
        matcher = NoAttributesTagElementMatcher(['a'])
        self.assertFalse(matcher.doesMatch(element))


class TestAttributeSubstringTagElementMatcher(unittest.TestCase):
    def test_all_substrings_match(self):
        matcher = AttributeSubstringTagElementMatcher(
            ['a'], ['href'], all_substrings=['str1', 'str2'],
        )
        self.assertTrue(matcher.doesMatch(Element('a', href="str1 str2")))
        self.assertFalse(matcher.doesMatch(Element('a', href="str1")))
        self.assertFalse(matcher.doesMatch(Element('b', href="str1 str2")))
        self.assertFalse(matcher.doesMatch(Element('a')))

    def test_any_substrings_match(self):
        matcher = AttributeSubstringTagElementMatcher(
            ['a'], ['href'], any_substrings=['str1', 'str2'],
        )
        self.assertTrue(matcher.doesMatch(Element('a', href="str1 str2")))
        self.assertTrue(matcher.doesMatch(Element('a', href="str1")))
        self.assertTrue(matcher.doesMatch(Element('a', href="str2")))
        self.assertFalse(matcher.doesMatch(Element('b', href="str1")))
        self.assertFalse(matcher.doesMatch(Element('a', href="str3")))
        self.assertFalse(matcher.doesMatch(Element('a')))

    def test_disallowed_substrings(self):
        matcher = AttributeSubstringTagElementMatcher(
            ['a'], ['href'], disallowed_substrings=['str1', 'str2'],
        )
        self.assertFalse(matcher.doesMatch(Element('a', href="str1 str2")))
        self.assertFalse(matcher.doesMatch(Element('a', href="str1")))
        self.assertFalse(matcher.doesMatch(Element('a', href="str2")))
        self.assertTrue(matcher.doesMatch(Element('a', href="str3")))
        self.assertFalse(matcher.doesMatch(Element('b', href="str1")))
        self.assertFalse(matcher.doesMatch(Element('a')))

    def test_combined(self):
        matcher = AttributeSubstringTagElementMatcher(
            ['a'], ['href'],
            all_substrings=['all1', 'all2'],
            any_substrings=['any1', 'any2'],
            disallowed_substrings=['bad1', 'bad2'],
        )
        def assertTrue(href):
            self.assertTrue(matcher.doesMatch(Element('a', href=href)))
        def assertFalse(href):
            self.assertFalse(matcher.doesMatch(Element('a', href=href)))

        assertTrue(href="all1 all2 any1")
        assertTrue(href="all1 all2 any2")
        assertTrue(href="all1 all2 any1 any2")
        assertFalse(href="all1 any1")
        assertFalse(href="all2 any1")
        assertFalse(href="all1 all2")
        assertFalse(href="all1 all2 any1 bad1")
        assertFalse(href="all1 all2 any1 bad2")
        assertFalse(href="bad1")
