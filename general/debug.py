import logging
import pprint

def logargs(*args):
    print(zip(args))

def logline(text):
    print('[{}]'.format(text))

def kwlog(**kwargs):
    print('((((')
    for name, obj in kwargs.iteritems():
        print('[{}]'.format(name))
        pp = pprint.PrettyPrinter(depth = 6)
        pp.pprint(obj)
        print('[/{}]'.format(name))
    print('))))')

def log(name, obj):
    print('[{}]'.format(name))
    pp = pprint.PrettyPrinter(depth = 6)
    pp.pprint(obj)
    print('[/{}]'.format(name))

def get_resolved_urls(url_patterns):
    url_patterns_resolved = []
    for entry in url_patterns:
        if hasattr(entry, 'url_patterns'):
            url_patterns_resolved += get_resolved_urls(entry.url_patterns)
        else:
            url_patterns_resolved.append(entry)
    return url_patterns_resolved
