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

def urlclean(path):
    if path[-1:] == '/':
        path = path[:-1]
    if path[:1] == '/':
        path = path[1:]
    return path
    
def urlsplit(path):
    return urlclean(path).split('/')

def urljoin(*args):
    return '/'.join([urlclean(_) for _ in args if len(_) > 0])