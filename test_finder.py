from general import debug, urljoin, urlclean, urlsplit

import unittest

import fnmatch, os

class TestBuilderCreator(unittest.TestCase):
    def test_urljoin(self):
        files = []

        for root, dirnames, filenames in os.walk('/srv/cloudarchive/content'):
            files.extend(fnmatch.filter(filenames, '*.py'))

        print(files)

        self.assertEqual('a', 'a')

if __name__ == '__main__':
    unittest.main()
