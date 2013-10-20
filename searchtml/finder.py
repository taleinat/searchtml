from searchtml.matchers import TagElementMatcher

__all__ = [
    'ElementFinder',
]


class ElementFinder(object):
    def __init__(self):
        self.ignore_element_matchers = []
        self.element_matchers = []

    def add_ignore_node_matcher(self, node_matcher):
        self.ignore_element_matchers.append(node_matcher)

    def add_node_matcher(self, node_matcher):
        self.element_matchers.append(node_matcher)

    def findElements(self, root_element):
        """Find all elements matching each element matcher.

        Elements matched by any element-matcher in ignore_element_matchers are
        skipped, including all of their descendants.

        An element may be matched by multiple element-matchers, and will be
        added to all relevant result lists.

        @param root_element: the element to begin search from
                             (must implement getchildren())
        @return: dict: element_matcher => list of matching elements
        """
        result_elements = {}
        for element_matcher in self.element_matchers:
            result_elements[element_matcher] = []

        non_tag_ignore_ems = []
        ignore_ems_by_tags = {}
        for em in self.ignore_element_matchers:
            if isinstance(em, TagElementMatcher):
                for tag in em.tags:
                    ignore_ems_by_tags.setdefault(tag.lower(), []).append(em)
            else:
                non_tag_ignore_ems.append(em)

        non_tag_match_ems = []
        match_ems_by_tags = {}
        for em in self.element_matchers:
            if isinstance(em, TagElementMatcher):
                for tag in em.tags:
                    match_ems_by_tags.setdefault(tag.lower(), []).append(em)
            else:
                non_tag_match_ems.append(em)

        stack = [root_element]
        while stack:
            element = stack.pop()

            # ignore special elements
            # (ProcessingInstructions, Comments and Entity instances)
            if not isinstance(element.tag, basestring):
                continue

            # ignore elements matched by any of self.ignore_element_matchers
            if any(
                    element_matcher.doesMatch(element)
                    for element_matcher in
                    non_tag_ignore_ems + ignore_ems_by_tags.get(element.tag.lower(), [])
            ):
                continue

            # continue iterating through the element's children later
            stack.extend(reversed(element.getchildren()))

            # run all of the relevant element-matchers on this element
            for element_matcher in non_tag_match_ems + match_ems_by_tags.get(element.tag.lower(), []):
                if element_matcher.doesMatch(element):
                    result_elements[element_matcher].append(element)

        return result_elements