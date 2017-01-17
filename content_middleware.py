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

from general import debug, urlclean, urljoin, urlsplit

from middleware import Middleware

class ContentMiddleware(Middleware):
    def get_manifests(self, context):
        """
        get list of manifests for assets not already in output
        """

        raw_file_array = context['assets']

        manifests = context['manifests']

        manifest_array = [_ for _ in raw_file_array if _['Category'] == 'manifest']

        rfd_selector_array = [_['rfd']['RelativePath'] for _ in manifest_array]

        return [_ for _ in manifests if _['related_selector'] not in (rfd_selector_array)]

 
class ID3TagMiddleware(ContentMiddleware):
    def create(self):
        def func(mwa, context):
            print('ID3TagMiddleware::process')
            try:
                import eyed3
            except:
                print('eyed3 not found')
                return

            context['pending_list'] = []
            for manifest_entry in self.get_manifests(context):
                manifest = manifest_entry['file_manifest']
                manifest_path = manifest['_filename']
                mp3_path = manifest_entry['related_filename']
                rfd = manifest_entry['rfd']

                data = eyed3.load(mp3_path)

                """
                debug.log('data.tag.artist', data.tag.artist)
                debug.log('data.tag.album', data.tag.album)
                debug.log('data.tag.album_artist', data.tag.album_artist)
                debug.log('data.tag.title', data.tag.title)
                debug.log('data.tag.track_num', data.tag.track_num)
                """

                changed = False

                try:
                    if data.tag.artist != manifest['artist']:
                        changed = True
                        print('artist')
                        data.tag.artist = unicode(manifest['artist'], 'utf-8')
                except KeyError:
                    pass

                try:
                    if data.tag.album != manifest['album']:
                        changed = True
                        print('album')
                        print('current:{}'.format(data.tag.album))
                        print('new:' + manifest['album'])
                        data.tag.album = unicode(manifest['album'], 'utf-8')
                except KeyError:
                    pass

                try:
                    if data.tag.album_artist != manifest['albumartist']:
                        changed = True
                        print('albumartist')
                        data.tag.albumartist = unicode(manifest['albumartist'], 'utf-8')
                except KeyError:
                    pass

                try:
                    if data.tag.title != manifest['title']:
                        changed = True
                        print('title')
                        data.tag.title = unicode(manifest['title'], 'utf-8')
                except KeyError:
                    pass
                try:
                    if data.tag.track_num != manifest['tarack'][0]:
                        changed = True
                        print('track')
                        print('current:{}'.format(data.tag.track_num))
                        print('new:' + manifest['track'])
                        data.tag.track_num = int(manifest['track'])
                except KeyError:
                    pass

                if changed:
                    data.tag.save()
                    """
                    debug.log('data.tag.artist', data.tag.artist)
                    debug.log('data.tag.album', data.tag.album)
                    debug.log('data.tag.album_artist', data.tag.album_artist)
                    debug.log('data.tag.title', data.tag.title)
                    debug.log('data.tag.track_num', data.tag.track_num)
                    """
                    context['pending_list'].append(rfd)

            return next(mwa)

        return func