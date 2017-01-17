"""
CloudArchivePy
Copyright (C) 2016-2017 David Betz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from general import debug, urljoin, urlclean, urlsplit

import unittest

class TestBuilderCreator(unittest.TestCase):
    def test_urljoin(self):
        base = '/srv/project'
        path = '/content/frog'

        self.assertEqual(urljoin(base, path), 'srv/project/content/frog')

    def test_urljoinmulti(self):
        base = 'srv'
        path1 = 'project/content'
        path2 = ''

        self.assertEqual(urljoin(path2, urljoin(base, path1)), 'srv/project/content')

    def test_urlclean(self):
        base = '/srv/project/'

        self.assertEqual(urlclean(base), 'srv/project')

    def test_urlsplit(self):
        self.assertListEqual(urlsplit('/srv/project/content/frog'), ['srv', 'project', 'content', 'frog'])

if __name__ == '__main__':
    unittest.main()
