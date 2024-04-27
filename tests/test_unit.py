import io
from http.cookiejar import CookieJar

import pytest
from requests.cookies import RequestsCookieJar

from assets import MockRequestBuilder, echo_function


@pytest.fixture()
def rb() -> MockRequestBuilder:
    return MockRequestBuilder('path')


def test_init_path():
    path = 'somepath'
    rb = MockRequestBuilder(path)
    assert rb._path == path


def test_init_known_kwargs():
    rb = MockRequestBuilder('path',
                            cert='cert',
                            proxies={'http': 'server'})
    assert rb.a._kwargs['cert'] == 'cert'
    assert rb.b._kwargs['proxies'] == {'http': 'server'}
    assert 'allow_redirects' not in rb.c._kwargs
    assert 'verify' not in rb.d._kwargs
    assert 'auth' not in rb.e._kwargs


def test_init_other_kwargs():
    rb = MockRequestBuilder('path', a=1, b=2, c=3, d=4)
    assert rb.a._kwargs == {'a': 1, 'b': 2, 'c': 3, 'd': 4}


def test_error_suppression():
    rb = MockRequestBuilder('path', suppress_errors=True)
    assert rb.a._suppress_errors


def test_getitem():
    rb = MockRequestBuilder('some')
    assert rb['path']._path == 'some/path'


def test_getattr():
    rb = MockRequestBuilder('some')
    assert rb.path._path == 'some/path'


def test_setattr(rb):
    rb._test = 'value'
    assert hasattr(rb, '_test')
    assert rb._test == 'value'

    assert rb._path == 'path'
    rb.path = 'another_path'
    assert rb._path == 'another_path'

    assert 'a' not in rb._kwargs
    rb.a = 1
    assert 'a' in rb._kwargs
    assert rb._kwargs['a'] == 1

    rb = rb(a='1')
    assert rb._kwargs['params'] == {'a': '1'}
    rb.params = {}
    assert rb._kwargs['params'] == {}


def test_data(rb):
    rb = rb(data='somedata')

    assert rb._kwargs['input_data'] == 'somedata'


def test_files(rb):
    rb = rb(files={'file1': io.StringIO('val1')})
    rb = rb(files={'file2': io.StringIO('val2')})
    assert len(rb._kwargs['files']) == 2
    assert rb._kwargs['files']['file1'].read() == 'val1'
    assert rb._kwargs['files']['file2'].read() == 'val2'


def test_auth(rb):
    rb = rb(auth='basic')
    assert rb._kwargs['auth'] == 'basic'
    rb = rb(auth='bearer')
    assert rb._kwargs['auth'] == 'bearer'


def test_headers(rb):
    rb = rb(headers={'X-Custom-Header-1': 'val1'})
    assert len(rb._kwargs['headers']) == 1
    rb = rb(headers={'X-Custom-Header-2': 'val2'})
    assert len(rb._kwargs['headers']) == 2


def test_timeout(rb):
    rb = rb(timeout=3.4)
    assert rb._kwargs['timeout'] == 3.4
    rb = rb(timeout=(1, 2))
    assert rb._kwargs['timeout'] == (1, 2)


def test_stream(rb):
    rb = rb(stream=True)
    assert rb._kwargs['stream']
    rb = rb(stream=False)
    assert not rb._kwargs['stream']


def test_cookies(rb):
    # Assign on None
    rb = rb(cookies=4.56)
    assert rb._kwargs['cookies'] == 4.56

    jar = RequestsCookieJar()
    jar.set('c1', 'v1')
    jar.set('c2', 'v2')

    # Assign on unknown type
    rb = rb(cookies=jar)
    assert len(rb._kwargs['cookies']) == 2
    assert isinstance(rb._kwargs['cookies'], CookieJar)

    # Assign dict on CookieJar
    rb = rb(cookies={'c3': 'v3'})
    assert len(rb._kwargs['cookies']) == 3
    assert isinstance(rb._kwargs['cookies'], dict)

    # Assign dict on dict
    rb = rb(cookies={'c4': 'v4'})
    assert len(rb._kwargs['cookies']) == 4

    # Assign CookieJar on dict
    jar2 = RequestsCookieJar()
    jar2.set('c5', 'v5')
    rb = rb(cookies=jar2)
    assert len(rb._kwargs['cookies']) == 5

    # Assign CookieJar on CookieJar
    rb.cookies = jar
    rb = rb(cookies=jar2)
    assert len(rb._kwargs['cookies']) == 3
    assert isinstance(rb._kwargs['cookies'], dict)


def test_params(rb):
    rb = rb(p1='v1')
    assert rb._kwargs['params'] == {'p1': 'v1'}
    rb = rb(p2='v2')
    assert rb._kwargs['params'] == {'p1': 'v1', 'p2': 'v2'}
    rb = rb(p3='v3', p4='v4')
    assert rb._kwargs['params'] == {'p1': 'v1', 'p2': 'v2', 'p3': 'v3', 'p4': 'v4'}


def test_send(rb):
    args, kwargs = echo_function / rb.another.bit('data', param1='value1', param2='value2')
    assert args == ('path/another/bit', )
    assert kwargs == {'input_data': 'data', 'params': {'param1': 'value1', 'param2': 'value2'}}


def test_mocked_send(rb, monkeypatch):
    monkeypatch.setattr('requests.request', echo_function)

    args, kwargs = 'GET' / rb.another.bit('data', param1='value1', param2='value2')
    assert args == ('GET', 'path/another/bit',)
    assert kwargs == {'input_data': 'data', 'params': {'param1': 'value1', 'param2': 'value2'}}


def test_processed_send(rb):
    args_len, kwargs_len = echo_function // rb.another.bit('data', param1='value1', param2='value2')
    assert args_len == 1
    assert kwargs_len == 2
