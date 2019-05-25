import logging
import json
import re
import os
from http.client import responses as status_codes
from urllib.parse import unquote, parse_qs
from inspect import signature
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger('burette')
status_headers = {code: '%d %s' % (code, status_codes[code]) for code in status_codes.keys()}


class Burette:
    """
    A micro web framework.

    """

    def __init__(self):
        self._router = Router()

    def __call__(self, env, start_response):
        request = Request(env)
        try:
            response = self._router.dispatch(request)
        except HttpError as e:
            start_response(status_headers[e.status_code], [self.make_content_type_header('text/html', request.charset)])
            return [e.body.encode(request.charset)]
        except Exception as e:
            logging.error(e)
            start_response(status_headers[500], [self.make_content_type_header('text/html', request.charset)])
            return ['<html><body>Internal Server Error</body></html>'.encode(request.charset)]

        response_body, status, headers = self.make_response(response, request.charset)
        start_response(status, headers)
        return [response_body]

    @staticmethod
    def make_content_type_header(content_type, charset):
        if content_type is None:
            content_type = 'text/html'
        if charset is None:
            charset = 'utf-8'

        return 'Content-Type', content_type + '; charset=' + charset

    def make_response(self, response, req_charset):
        """
        :param response: Response, dict, or str
        :param req_charset: request charset
        :return: a tuple that has (response body, status line, headers)
        """
        if type(response) is Response:
            charset = response.charset
            response_body = response.body
            status = status_headers[response.status]
            headers = response.headers
            headers.append(self.make_content_type_header(response.content_type, charset))
            if response.status == 302:
                headers.append(('Location', response.location_url))
        elif type(response) is dict:
            charset = req_charset
            response_body = json.dumps(response)
            status = status_headers[200]
            headers = [self.make_content_type_header('application/json', charset)]
        else:
            charset = req_charset
            response_body = response if response is not None else ''
            status = status_headers[200]
            headers = [self.make_content_type_header('text/html', charset)]

        return response_body.encode(charset), status, headers

    def route(self, path, method='GET'):
        """
        decorator to add a route.

        :param path: routing path.
        :param method: 'GET', 'POST', or 'PUT'
        :return:
        """
        def decorator(callback):
            arg_len = len(signature(callback).parameters)
            self._router.add_route(Route(path, method, callback, arg_len))
            return callback

        return decorator

    def run_local(self, host='localhost', port=5963):
        """
        Run the development mode server.
        Not for production use.
        """
        from wsgiref.simple_server import make_server
        logging.info('RUN_LOCAL ' + host + ':' + str(port))
        server = make_server(host, port, self)
        server.serve_forever()


class Response:
    """
    Response
    """
    def __init__(self):
        self.content_type = 'text/html'
        self.charset = 'utf-8'
        self.status = 200
        self.body = ''
        self.headers = []


class Request:
    """
    Request
    """
    def __init__(self, env):
        self.path = env.get('PATH_INFO')
        self.method = env.get('REQUEST_METHOD')
        self._env = env
        self._content_type_line = env.get('CONTENT_TYPE', '').split('charset=')
        self._body = bytes()
        self._text = ''

    @property
    def params(self):
        return parse_qs(self._env.get('QUERY_STRING'))

    @property
    def content_type(self):
        return self._content_type_line[0].split(';')[0].strip()

    @property
    def charset(self):
        return self._content_type_line[1].strip(' "') if len(self._content_type_line) > 1 else 'UTF-8'

    @property
    def content_length(self):
        return int(self._env.get('CONTENT_LENGTH', 0))

    @property
    def body(self):
        if not self._body:
            self._body = self._env.get('wsgi.input').read(self.content_length)
        return self._body

    @property
    def text(self):
        if not self._text:
            self._text = unquote(self.body.decode(self.charset))
        return self._text


class Router:
    """
    Router.
    """
    def __init__(self):
        self._routes = []

    def add_route(self, route):
        self._routes.append(route)

    def dispatch(self, request):
        route, path_params = self._match(request.path, request.method)
        request.path_params = path_params
        if route.use_arg:
            return route.callback(request)
        return route.callback()

    def _match(self, path, method):
        for r in self._routes:
            path_params = r.match(path)
            if path_params is not None and r.method == method:
                return r, path_params
        if path_params is not None:
            raise HttpError(405, '<html><body>method not allowed</body></html>')

        raise HttpError(404, '<html><body>not found</body></html>')


class Route:
    """
    Route.
    """

    _key_pattern = re.compile('(<[a-zA-Z_][a-zA-Z0-9_]*>)')

    def __init__(self, path, method, callback, use_arg):
        self.path = path
        self.method = method
        self.callback = callback
        self.use_arg = use_arg
        self._make_rule(path)

    def _make_rule(self, path):
        self._keys = []
        pattern = path
        try:
            for match in self._key_pattern.finditer(path):
                key = match.group(1)
                pattern = re.sub(key, '(?P' + key + '[a-zA-Z0-9_]+)', pattern)
                self._keys.append(key[1:-1])

            self._pattern = re.compile('^' + pattern + '$')
        except Exception:
            raise Exception('Failed to add route. please check the path syntax')

    def match(self, path):
        """
        :param path:
        :return: path param dictionary {key:paramter} or None
        """
        m = self._pattern.search(path)
        if not m:
            return None
        path_params = {}
        for key in self._keys:
            path_params[key] = m.group(key)
        return path_params


class HttpError(Exception):
    """
    exception that may or may not be thrown from the application
    """
    def __init__(self, status_code, body=''):
        self.status_code = status_code
        self.body = body


def redirect(location_url):
    response = Response()
    response.location_url = location_url
    response.status = 302
    return response


def jinja2(template_filename, **kwargs):
    try:
        template_path = kwargs.pop('template_path', './templates')
        folder = os.path.abspath(template_path)
        env = Environment(loader=FileSystemLoader(folder, encoding=kwargs.pop('encoding', 'utf-8'), followlinks=True))
        template = env.get_template(template_filename)
        return template.render(**kwargs)
    except Exception as e:
        logging.error('Failed to load the template {template_filename}.'.format(template_filename=template_filename))
        raise e
