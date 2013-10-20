__all__ = [
    'ElementMatcher',
    'TagElementMatcher',
    'NoAttributesTagElementMatcher',
    'AttributeSubstringTagElementMatcher',
]


class ElementMatcher(object):
    """Abstract base class for element matchers"""
    def doesMatch(self, element):
        raise NotImplementedError


class TagElementMatcher(ElementMatcher):
    def __init__(self, tags):
        if isinstance(tags, basestring):
            msg = 'The tags parameter must be a collection of strings.'
            raise TypeError(msg)
        self.tags = frozenset(tag.lower() for tag in tags)

    def doesMatch(self, element):
        return element.tag.lower() in self.tags


class NoAttributesTagElementMatcher(TagElementMatcher):
    def doesMatch(self, element):
        return (not element.attrib) and \
            super(NoAttributesTagElementMatcher, self).doesMatch(element)


class AttributeSubstringTagElementMatcher(TagElementMatcher):
    def __init__(self, tags, attributes, all_substrings=None, any_substrings=None, disallowed_substrings=None):
        super(AttributeSubstringTagElementMatcher, self).__init__(tags)

        self.attributes = frozenset(attr.lower() for attr in attributes)
        self.all_substrings = frozenset(substr.lower() for substr in (all_substrings if all_substrings is not None else []))
        self.any_substrings = frozenset(substr.lower() for substr in (any_substrings if any_substrings is not None else []))
        self.disallowed_substrings = frozenset(substr.lower() for substr in (disallowed_substrings if disallowed_substrings is not None else []))

    def doesMatch(self, element):
        if not super(AttributeSubstringTagElementMatcher, self).doesMatch(element):
            return False
        for attr in self.attributes.intersection(element.attrib):
            attr_value = element.attrib[attr].lower()
            if (
                all(ss in attr_value for ss in self.all_substrings) and
                not any(ss in attr_value for ss in self.disallowed_substrings) and
                (any(ss in attr_value for ss in self.any_substrings) if self.any_substrings else True)
            ):
                return True
        return False
