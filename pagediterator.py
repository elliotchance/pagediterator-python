class PagedIterator:
    """A PagesIterator lets you define an iterator that's made up of multiple
    pages of the same size (except for the last one).

    Example:

        class MyPagedIterator(PagedIterator):
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

    Now you can operate on it just as if were an array or iterator:

        iterator = new MyPagedIterator();
        print iterator[4] # 5

        for item in iterator:
            print item
        # 1 2 3 4 5 6 7 8

    It's important to note that pages are cached internally after first access.
    This makes it ideal for APIs that will only do one API request per page no
    matter what the items order requested is:

        import urllib

        class GithubSearcher(PagedIterator):
            def __init__(self, search_term):
                self.total_size = 0
                self.search_term = search_term

                # this will make sure totalSize is set before we try and access
                # the data
                self.get_page(0)

            @property
            def total_size(self):
                return self.total_size

            @property
            def page_size(self):
                return 100

            def get_page(self, page_number):
                q = urllib.urlencode({
                    'q': 'fridge',
                    'page': page_number + 1
                })
                url = "https://api.github.com/search/repositories?" + q

                result = json.loads(urllib2.urlopen(url).read())
                self.total_size = result['total_count']
                return result['items']

        repositories = GithubSearcher('fridge')
        print "Found %d results:" % len(repositories)
        for repo in repositories:
            print repo['full_name']

    """
    def __init__(self):
        """Create a new paged iterator."""
        self.cached_pages = {}
        self.index = 0

    @property
    def page_size(self):
        """Get the size of a single page.

        Note:
          This needs to be overridden by the child class.

        Returns:
          int - Which must return a constant value between calls as pages must
          always been a fixed and equal size.
        """
        raise RuntimeError("page_size() must be implemented.")

    @property
    def total_size(self):
        """Get the total number of items. This will dictate how many pages
        there will be by inference.

        Note:
          This needs to be overridden by the child class.

        Returns:
          int
        """
        return 0

    def get_page(self, page_number):
        """Return a page at a given index.

        Note:
          This needs to be overridden by the child class.

        Returns:
          list
        """
        raise RuntimeError("get_page() must be implemented.")

    def __len__(self):
        """Return the total length. This allows the use of the `len()` on a
        `PagedIterator`.

        Returns:
          int
        """
        return self.total_size

    def __contains__(self, offset):
        """Test if an index is valid.

        Args:
          offset (int) - The array index.

        """
        assert isinstance(offset, int)

        return offset >= 0 and offset < len(self)

    def __getitem__(self, offset):
        """Fetch an item from the iterator at an arbitrary point.

        Args:
          offset (int) - The array index.

        Returns:
          Any value at the index.

        """
        if not isinstance(offset, int):
            raise ValueError("Index must be a positive integer: %s" % offset)

        if offset not in self:
            raise IndexError("Index out of bounds: %s" % offset)

        page = (int) (offset / self.page_size)
        if page not in self.cached_pages:
            self.cached_pages[page] = self.get_page(page)

        return self.cached_pages[page][offset % self.page_size]

    def __setitem__(self, key, value):
        """You cannot set items of the iterator."""
        raise RuntimeError("Setting values is not allowed.")

    def __delitem__(self, key):
        """You cannot delete items from an iterator."""
        raise RuntimeError("Unsetting values is not allowed.")

    def __iter__(self):
        """Get the iterator instance."""
        self.index = 0
        return self

    def next(self):
        """Get the next value for the iterator.

        Returns:
          The next value, or a `StopIteration` is raised.

        """
        assert isinstance(self.total_size, int)

        if self.index >= self.total_size:
            raise StopIteration

        self.index += 1
        return self[self.index - 1]

    def __next__(self):
        """This is for Python 3 and is an alias for the older `next()`."""
        return self.next()
