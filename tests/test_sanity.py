import os
from xml.etree import ElementTree

import pytest

from assets import ECHO_ENDPOINT_URL
from request_builder import XMLRequestBuilder
from request_builder.json_request_builder import JSONRequestBuilder
from request_builder.raw_request_builder import RequestBuilder
from tests.assets import ECHO_ENDPOINT_URL, XML_ENDPOINT_URL


@pytest.fixture()
def rb() -> RequestBuilder:
    return RequestBuilder(ECHO_ENDPOINT_URL)


@pytest.fixture()
def json_rb() -> JSONRequestBuilder:
    return JSONRequestBuilder(ECHO_ENDPOINT_URL)


def test_get(json_rb):
    response = 'GET' // json_rb
    assert response['path'] == '/'
    assert response['method'] == 'GET'
    assert response['parsedQueryParams'] == {}


def test_get_path(json_rb):
    response = 'GET' // json_rb.a.b.c.d
    assert response['path'] == '/a/b/c/d'

    response = 'GET' // json_rb['abc']['def']
    assert response['path'] == '/abc/def'


def test_get_query_params(json_rb):
    response = 'GET' // json_rb(a=1, b=2, c=3, d=4)
    assert response['parsedQueryParams'] == {'a': '1', 'b': '2', 'c': '3', 'd': '4'}

    mrb = json_rb(a=4, b=3)
    mrb = mrb(c=2, d=1)
    response = 'GET' // mrb
    assert response['parsedQueryParams'] == {'a': '4', 'b': '3', 'c': '2', 'd': '1'}


def test_get_headers(json_rb):
    response = 'GET' // json_rb(headers={'X-Custom-Header-1': 'val1',
                                         'X-Custom-Header-2': 'val2'})
    assert response['headers']['X-Custom-Header-1'] == 'val1'
    assert response['headers']['X-Custom-Header-2'] == 'val2'

    mrb = json_rb(headers={'X-Custom-Header-3': 'val4'})
    mrb = mrb(headers={'X-Custom-Header-4': 'val3'})
    response = 'GET' // mrb
    assert response['headers']['X-Custom-Header-3'] == 'val4'
    assert response['headers']['X-Custom-Header-4'] == 'val3'


def test_post_json(json_rb):
    data = {
        'a': 1, 'b': 'stringval', 'c': None,
        'd': True, 'e': 4.53, 'f': [1, 't', 3],
        'g': {'h': 1, 'i': 16.7}
    }
    response = 'POST' // json_rb(data)
    assert response['parsedBody'] == data


def test_post_file(rb):
    response = 'POST' / rb(data=open(r'assets/test_file.txt', 'rb'))
    response_json = response.json()
    assert response_json['headers']['Content-Length'] == str(os.stat(r'assets/test_file.txt').st_size)
    assert len(response_json['rawBody']) == os.stat(r'assets/test_file.txt').st_size


def test_post_form_data(rb):
    data = {'field1': 'val1', 'field2': 'val2'}
    response = 'POST' / rb(data, files={'file': open(r'assets/test_file.txt', 'rb')})
    response_json = response.json()
    assert response_json['headers']['Content-Type'].startswith('multipart/form-data')
    assert response_json['parsedBody']['textFields'] == data
    assert response_json['parsedBody']['files'][0]['name'] == 'file'
    assert response_json['parsedBody']['files'][0]['fileName'] == 'test_file.txt'


@pytest.mark.parametrize('method', ['PATCH', 'DELETE', 'PUT'])
def test_other_methods(json_rb, method: str):
    assert (method // json_rb)['method'] == method


def test_xml_send():
    rb = XMLRequestBuilder(ECHO_ENDPOINT_URL)
    data = ElementTree.Element('sample-tag', {'attr1': 'a', 'attr2': 'b'})
    data.text = 'content'
    response = 'POST' / rb(data)
    response_json = response.json()
    assert response_json['rawBody'] == '<sample-tag attr1="a" attr2="b">content</sample-tag>'


def test_xml_receive():
    rb = XMLRequestBuilder(XML_ENDPOINT_URL, suppress_errors=True)
    response = 'GET' // rb
    assert response.attrib['author'] == 'Yours Truly'
