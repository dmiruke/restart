from __future__ import absolute_import

import pytest
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request as WerkzeugSpecificRequest

from restart.config import config
from restart.resource import Resource
from restart.request import WerkzeugRequest
from restart.response import Response, WerkzeugResponse
from restart.exceptions import HTTPException


def fake_werkzeug_request(method='GET', url='/', data='',
                          content_type='application/json'):
    if '?' in url:
        path, query_string = url.split('?')
    else:
        path, query_string = url, None
    builder = EnvironBuilder(path=path, query_string=query_string,
                             method=method, data=data,
                             content_type=content_type)
    environ = builder.get_environ()
    initial_request = WerkzeugSpecificRequest(environ)
    request = WerkzeugRequest(initial_request)
    return request


class EchoResource(Resource):
    name = 'echo'

    def read(self, request):
        return request.data

    def create(self, request):
        raise Exception('Error occurs')


class TestResource(object):

    def make_resource(self, action_map=config.ACTION_MAP):
        return EchoResource(action_map)

    def test_dispatch_request(self):
        data = '"hello"'
        request = fake_werkzeug_request(data=data)
        resource = self.make_resource()
        response = resource.dispatch_request(request)

        assert isinstance(response, Response)
        assert response.data == data
        assert response.status_code == 200

    def test_dispatch_request_with_invalid_action_map(self):
        data = '"hello"'
        request = fake_werkzeug_request(data=data)
        resource = self.make_resource(action_map={'POST': 'create'})

        with pytest.raises(KeyError) as exc:
            resource.dispatch_request(request)
        expected_exc_msg = "Config `ACTION_MAP` has no mapping for 'GET'"
        assert str(exc.value) == repr(expected_exc_msg)

    def test_dispatch_request_with_unimplemented_action(self):
        data = '"hello"'
        request = fake_werkzeug_request(method='PATCH', data=data)
        resource = self.make_resource()

        with pytest.raises(AttributeError) as exc:
            resource.dispatch_request(request)
        expected_exc_msg = "Unimplemented action 'update'"
        assert str(exc.value) == expected_exc_msg

    def test_dispatch_request_with_action_exception(self):
        data = '"hello"'
        request = fake_werkzeug_request(method='POST', data=data)
        resource = self.make_resource()

        with pytest.raises(Exception) as exc:
            resource.dispatch_request(request)
        expected_exc_msg = 'Error occurs'
        assert str(exc.value) == expected_exc_msg

    def test_handle_exception_with_exception(self):
        resource = self.make_resource()
        resource.request = fake_werkzeug_request()
        with pytest.raises(Exception):
            resource.handle_exception(Exception())

    def test_handle_exception_with_httpexception(self):
        resource = self.make_resource()
        resource.request = fake_werkzeug_request()
        exc = HTTPException()
        rv = resource.handle_exception(exc)
        assert rv == ({'message': None}, None, {'Content-Type': 'text/html'})

    def test_make_response_with_data(self):
        rv = {'hello': 'world'}
        resource = self.make_resource()
        response = resource.make_response(rv)

        assert isinstance(response, Response)
        assert response.data == rv
        assert response.status_code == 200
        assert response.headers == {}

    def test_make_response_with_data_status(self):
        rv = {'hello': 'world'}, 204
        resource = self.make_resource()
        response = resource.make_response(rv)

        assert isinstance(response, Response)
        assert response.data == rv[0]
        assert response.status_code == rv[1]
        assert response.headers == {}

    def test_make_response_with_data_status_headers(self):
        rv = {'hello': 'world'}, 204, {'HOST': 'www.test.com'}
        resource = self.make_resource()
        response = resource.make_response(rv)

        assert isinstance(response, Response)
        assert response.data == rv[0]
        assert response.status_code == rv[1]
        assert response.headers == rv[2]

    def test_make_response_with_response(self):
        rv = WerkzeugResponse({'hello': 'world'}, 204,
                              {'HOST': 'www.test.com'})
        resource = self.make_resource()
        response = resource.make_response(rv)

        assert isinstance(response, Response)
        assert response.data == rv.data
        assert response.status_code == rv.status_code
        assert response.status == rv.status
        assert response.headers == rv.headers
