from collections import namedtuple
from collections.abc import Iterable
from types import MethodType
from urllib.parse import parse_qs

import pytest
import requests
import responses
import json
from cnct import ConnectClient


ConnectResponse = namedtuple('ConnectResponse', ('count', 'query', 'value', 'status', 'exception'))


def _get_mock_url(url, kwargs, query=None):
    mock_url = url
    if '?' in url:
        if query:
            mock_url, _ = url.split('?')
            mock_url = f'{mock_url}?{query}'
        qs = parse_qs(url.split('?')[1], keep_blank_values=True)
        for k in qs.keys():
            if k.startswith('ordering(') or k.startswith('select('):
                mock_url = f'{mock_url}&{k}'

    if kwargs and 'params' in kwargs:
        limit = kwargs['params']['limit']
        offset = kwargs['params']['offset']
        mock_url = f'{mock_url}&limit={limit}&offset={offset}'

    return mock_url


@pytest.fixture
def response():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def progress(mocker):
    return mocker.MagicMock()


@pytest.fixture
def response_factory():
    def _create_response(count=None, query=None, value=None, status=None, exception=None):
        return ConnectResponse(count, query, value, status, exception)
    return _create_response


@pytest.fixture
def client_factory(mocker, response):
    def _create_client(connect_responses):
        response_iterator = iter(connect_responses)

        def _execute_http_call(self, method, url, kwargs):
            res = next(response_iterator)
            mock_url = _get_mock_url(url, kwargs, query=res.query)
            mock_kwargs = {}
            if res.count:
                mock_kwargs['status'] = 200
                mock_kwargs['headers'] = {'Content-Range': f'items 0-{res.count - 1}/{res.count}'}
                mock_kwargs['json'] = []

            if isinstance(res.value, Iterable):

                count = len(res.value)
                mock_kwargs['status'] = 200
                mock_kwargs['json'] = res.value
                mock_kwargs['headers'] = {
                    'Content-Range': f'items 0-{count-1}/{count}'
                }
            elif isinstance(res.value, dict):
                mock_kwargs['status'] = res.status or 200
                mock_kwargs['json'] = res.value
            elif res.value is None:
                if res.exception:
                    mock_kwargs['side_effect'] = res.exception
                else:
                    mock_kwargs['status'] = res.status
            else:
                mock_kwargs['status'] = res.status or 200
                mock_kwargs['body'] = str(res.value)
            response.add(
                method.upper(),
                mock_url,
                **mock_kwargs,
            )

            self.response = requests.request(method, url, **kwargs)
            if self.response.status_code >= 400:
                self.response.raise_for_status()

        client = ConnectClient('Key', use_specs=False)
        client._execute_http_call = MethodType(_execute_http_call, client)
        return client
    return _create_client


@pytest.fixture
def ff_request():
    with open('./tests/fixtures/ff_request.json') as request:
        return json.load(request)
