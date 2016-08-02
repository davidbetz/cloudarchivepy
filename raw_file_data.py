import os
import hashlib
import base64
import json

class RawFileData():
    def __init__(self, fullname):
        self._fullname = fullname
        self._data = {}
        self._content = None

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        out = []
        for x,y in self._data.iteritems():
            if isinstance(y, RawFileData):
                out.append('(((({}'.format(x))
                out.append('{}'.format(y))
                out.append('))))')
            else:
                out.append('{}:{}'.format(x, json.dumps(y, indent=4, sort_keys=True)))

        return '\n'.join(out)

    @property
    def json(self):
        return json.dumps(self, indent=4, sort_keys=True)

    def __iter__(self):
        return self._data.iteritems()

    @property
    def is_manifest(self):
        # Manifests don't have Manifest
        return 'Manifest' not in self._data  

    @property
    def fullname(self):
        return self._fullname

    def dump(self):
        return self._data

    def hash(self):
        return base64.b64encode(hashlib.md5(self.read()).digest())

    def read(self):
        if self._content is not None:
            return self._content
        if os.path.exists(self._fullname):
            with open(self._fullname, 'rb') as f:
                self._content = f.read()
                return self._content
        else:
            return None
