def urlclean(path):
    if path[-1:] == '/':
        path = path[:-1]
    if path[:1] == '/':
        path = path[1:]
    return path
    
def urlsplit(path):
    return urlclean(path).split('/')

def urljoin(*args):
    return '/'.join([urlclean(_) for _ in args])