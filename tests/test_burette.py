# -*- coding: utf-8 -*-

from burette import Burette

import pytest


@pytest.mark.parametrize('route_path, route_method, request_path, request_method, expected', [
    ('/get_url', 'GET', '/get_url', 'GET', '200 OK'),
    ('/post_url', 'POST', '/post_url', 'POST', '200 OK'),
    ('/put_url', 'PUT', '/put_url', 'PUT', '200 OK'),
    ('/hoge_url', 'HOGE', '/hoge_url', 'HOGE', '200 OK'),
    ('/get_url', None, '/get_url', 'GET', '405 Method Not Allowed'),
    ('/put_url', None, '/put_url', 'PUT', '405 Method Not Allowed'),
    ('/post_url', None, '/post_url', 'POST', '405 Method Not Allowed'),
    ('/get_url', 'GET', '/get_url_wrong', 'GET', '404 Not Found'),
    ('/post_url', 'POST', '/post_url_wrong', 'POST', '404 Not Found'),
    ('/put_url', 'PUT', '/put_url_wrong', 'PUT', '404 Not Found'),
    ('/get_url', 'GET', '/get_url', 'PUT', '405 Method Not Allowed'),
    ('/post_url', 'POST', '/post_url', 'PUT', '405 Method Not Allowed'),
    ('/put_url', 'PUT', '/put_url', 'GET', '405 Method Not Allowed'),
    ('/get_url', 'GET', '/get_url/', 'GET', '404 Not Found'),

])
def test_route(route_path, route_method, request_path, request_method, expected):
    app = Burette()

    @app.route(route_path, method=route_method)
    def test_routing():
        pass

    def start_response_callback(status, headers):
        assert(status == expected)

    env = {
        'REQUEST_METHOD': request_method,
        'PATH_INFO': request_path
    }

    app(env, start_response_callback)


def test_isp():

    app = Burette()
    @app.route('/get_url')
    def get_url():
        raise Exception()

    def start_response_callback(status, headers):
        assert(status == '500 Internal Server Error')
    env = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/get_url'
    }
    app(env, start_response_callback)


@pytest.mark.parametrize('route_path, route_method', [
    ('/get_url', 'GET'),
    ('/put_url', 'PUT'),
    ('/post_url', 'POST'),
    ('/unknown', 'UNKNOWN')
])
def test_request(route_path, route_method):
    app = Burette()

    @app.route(route_path, method=route_method)
    def get_url(request):
        assert(request.path == route_path)
        assert(request.method == route_method)
        return ''

    def start_response_callback(status, headers):
        assert(status == '200 OK')
    env = {
        'REQUEST_METHOD': route_method,
        'PATH_INFO': route_path
    }
    app(env, start_response_callback)


@pytest.mark.parametrize('route_path, query_string, params', [
    ('/get_url', 'akey=aval&bkey=bval', {'akey': ['aval'], 'bkey': ['bval']}),
    ('/get_url', 'akey=aval&akey=aval2', {'akey': ['aval', 'aval2']}),
    ('/get_url', 'akey=aval&bkey=bval&akey=aval2&ckey=', {'akey': ['aval', 'aval2'], 'bkey': ['bval']}),
    ('/get_url', 'akey=aval', {'akey': ['aval']}),
    ('/get_url', 'akey=aval&bkey=bval', {'akey': ['aval'], 'bkey': ['bval']}),
    ('/get_url', 'akey=%2F%23%3F%26&%2F%23%3F%26=bval', {'akey': ['/#?&'], '/#?&': ['bval']}),
])
def test_request_params(route_path, query_string, params):
    app = Burette()

    @app.route(route_path)
    def get_url(request):
        assert(request.path == route_path)
        assert(request.method == 'GET')
        assert(request.params == params)
        return ''

    def start_response_callback(status, headers):
        assert(status == '200 OK')
    env = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': route_path,
        'QUERY_STRING': query_string
    }
    app(env, start_response_callback)


@pytest.mark.parametrize('route_path, request_path, path_params', [
    ('/get_url/<param_key>', '/get_url/testvalue', {'param_key': 'testvalue'}),
    ('/get_url/<param_key>/', '/get_url/testvalue/', {'param_key': 'testvalue'}),
    ('/get_url/<param_key>/<param_key2>/', '/get_url/test/test2/', {'param_key': 'test', 'param_key2': 'test2'}),
])
def test_request_path_params(route_path, request_path, path_params):
    app = Burette()

    @app.route(route_path)
    def get_url(request):
        assert(request.path == request_path)
        assert(request.method == 'GET')
        assert(request.path_params == path_params)
        return ''

    def start_response_callback(status, headers):
        assert(status == '200 OK')
    env = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': request_path,
    }
    app(env, start_response_callback)


@pytest.mark.parametrize('route_path, request_path', [
    ('/get_url/<param_key>', '/get_url/testvalue/'),
    ('/get_url/<param_key>/abc', '/get_url/testvalue/'),
    ('/get_url/<param_key>/<param_key2>/', 'abc/get_url/testvalue/testvalue2/'),
    ('/get_url/<123abc>', '/get_url/testvalue/'),
])
def test_request_path_params_not_found(route_path, request_path):
    app = Burette()

    @app.route(route_path)
    def get_url():
        assert False
        return ''

    def start_response_callback(status, headers):
        assert(status == '404 Not Found')
    env = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': request_path,
    }
    app(env, start_response_callback)


@pytest.mark.parametrize('encoding, expected', [
    ('EUC-JP', 'EUC-JP'),
    ('UTF-8', 'UTF-8'),
    (None, 'UTF-8'),
])
def test_request_charset(encoding, expected):
    app = Burette()

    @app.route('/get_url', method='POST')
    def get_url(request):
        assert(request.charset == expected)
        assert(request.text == 'あいうえお')
        assert(request.body.decode(encoding=expected) == 'あいうえお')
        return 'かきくけこ'

    class Reader:
        def read(self, length):
            return 'あいうえお'.encode(encoding=expected)

    def start_response_callback(status, headers):
        assert(status == '200 OK')
        found = False
        for header_name, header_value in headers:
            if header_name == 'Content-Type':
                found = True
                assert(header_value == 'text/html; charset=' + expected)
        assert found

    content_type = 'text/plain; charset=' + encoding if encoding is not None else 'text/plain'
    env = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/get_url',
        'CONTENT_TYPE': content_type,
        'wsgi.input': Reader()
    }
    app(env, start_response_callback)
