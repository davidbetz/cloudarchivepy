from content_middleware import ID3TagMiddleware

config_location = 'cloudarchive.config.yaml'
max_threads = 1

middleware = [
    ('mp3', [ID3TagMiddleware])
]