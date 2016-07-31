def logargs(*args):
    print(zip(args))

def logline(text):
    print('[{}]'.format(text))

def log(name, obj):
    from pprint import pprint as pp
    print('[{}]'.format(name))
    pp(obj, depth = 6)
    print('[/{}]'.format(name))

def kwlog(**kwargs):
    print('((((')
    for name, obj in kwargs.iteritems():
        log(name, obj)
    print('))))')