from pagediterator import PagedIterator
from unittest import TestCase
from mock import MagicMock, call

class PagedIterator1(PagedIterator):
    def __init__(self):
        PagedIterator.__init__(self)
        self.fetch_page(0)

    @property
    def total_size(self):
        return self._total_size

    @property
    def page_size(self):
        return self._page_size

    def fetch_page(self, page_number):
        self._total_size = 8
        self._page_size = 3
        pages = [
            [ 1, 2, 3 ],
            [ 4, 5, 6 ],
            [ 7, 8 ],
        ]
        return pages[page_number]

    def get_page(self, page_number):
        return self.fetch_page(page_number)


class PagedIteratorTest(TestCase):
    def setUp(self):
        self.iterator = PagedIterator1()

    def test_count_returns_an_integer(self):
        self.assertEqual(len(self.iterator), 8)

    def test_fetching_a_negative_index_throws_an_exception(self):
        self.assertRaises(IndexError, self.iterator.__getitem__, -1)

    def test_fetching_an_out_of_bounds_index_throws_exception(self):
        self.assertRaises(IndexError, self.iterator.__getitem__, 15)

    def test_a_page_size_must_be_set(self):
        self.assertEqual(self.iterator.page_size, 3)

    def test_get_first_element(self):
        self.assertEqual(self.iterator[0], 1)

    def test_get_second_element(self):
        self.assertEqual(self.iterator[1], 2)

    def test_get_first_element_on_second_page(self):
        self.assertEqual(self.iterator[3], 4)

    def test_get_second_element_on_third_page(self):
        self.assertEqual(self.iterator[7], 8)

    def test_fetching_a_string_index_is_not_allowed(self):
        self.assertRaises(ValueError, self.iterator.__getitem__, 'foo')

    def test_offset_that_is_valid_returns_true(self):
        self.assertEqual(self.iterator[0], True)

    def test_offset_that_is_out_of_bounds_returns_false(self):
        self.assertEqual(15 in self.iterator, False)

    def test_offset_that_is_after_the_last_element_returns_false(self):
        self.assertEqual(10 in self.iterator, False)

    def test_values_of_the_same_index_are_cached(self):
        self.iterator.get_page = MagicMock(return_value=[1])
        self.assertEqual(self.iterator[0], 1)
        self.assertEqual(self.iterator[0], 1)
        self.iterator.get_page.assert_called_once_with(0)

    def test_values_of_the_same_pages_are_cached(self):
        self.iterator.get_page = MagicMock(return_value=[1, 2])
        self.assertEqual(self.iterator[0], 1)
        self.assertEqual(self.iterator[1], 2)
        self.iterator.get_page.assert_called_once_with(0)

    def test_values_from_another_page_must_be_requested(self):
        self.iterator.get_page = MagicMock(side_effect=[
            [1, 2, 3],
            [4, 5, 6],
        ])
        self.assertEqual(self.iterator[0], 1)
        self.assertEqual(self.iterator[3], 4)

    def test_values_from_multiple_pages_are_simultaneously_cached(self):
        self.iterator.get_page = MagicMock(side_effect=[
            [1, 2, 3],
            [4, 5, 6],
        ])
        self.assertEqual(self.iterator[0], 1)
        self.assertEqual(self.iterator[3], 4)
        self.assertEqual(self.iterator[0], 1)
        self.assertEqual(self.iterator[3], 4)
        self.iterator.get_page.assert_has_calls([call(0), call(1)])

    def test_traverse_list_in_loop(self):
        result = []
        for item in self.iterator:
            result.append(item)
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7, 8])

    def test_traverse_list_in_multiple_loops(self):
        result = []
        for item in self.iterator:
            result.append(item)
        for item in self.iterator:
            result.append(item)
        self.assertEqual(result, [
            1, 2, 3, 4, 5, 6, 7, 8,
            1, 2, 3, 4, 5, 6, 7, 8
        ])

    def test_setting_an_element_raises_an_exception(self):
        self.assertRaises(RuntimeError, self.iterator.__setitem__, 0, 0)

    def test_unsetting_an_element_raises_an_exception(self):
        self.assertRaises(RuntimeError, self.iterator.__delitem__, 0)
