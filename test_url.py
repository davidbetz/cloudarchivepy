from general import debug, urljoin, urlclean, urlsplit

import unittest

class TestBuilderCreator(unittest.TestCase):
    def test_urljoin(self):
        base = '/srv/project'
        path = '/content/frog'

        self.assertEqual(urljoin(base, path), 'srv/project/content/frog')

    def test_urlclean(self):
        base = '/srv/project/'

        self.assertEqual(urlclean(base), 'srv/project')

    def test_urlsplit(self):
        self.assertListEqual(urlsplit('/srv/project/content/frog'), ['srv', 'project', 'content', 'frog'])

if __name__ == '__main__':
    unittest.main()
