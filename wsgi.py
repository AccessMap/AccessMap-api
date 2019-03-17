from werkzeug.contrib.fixers import ProxyFix

from accessmapapi import create_app


class ReverseProxied:
    def __init__(self, wsgi_app, prefix):
        self.wsgi_app = wsgi_app
        self.prefix = prefix
        self.wsgi_app = ProxyFix(self.wsgi_app)

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = self.prefix
        path_info = environ['PATH_INFO']
        if path_info.startswith(self.prefix):
            environ['PATH_INFO'] = path_info[len(self.prefix):]

        return self.wsgi_app(environ, start_response)


def build_app(endpoint="/api"):
    app = create_app()
    app.wsgi_app = ReverseProxied(app.wsgi_app, endpoint)
    return app
