# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue
# All rights reserved.
#
import json
import os
from collections import namedtuple
from collections.abc import Iterable
from types import MethodType
from urllib.parse import parse_qs

import pytest
import requests
import responses
from connect.client import ConnectClient


ConnectResponse = namedtuple(
    'ConnectResponse',
    (
        'count', 'query', 'ordering', 'select',
        'value', 'status', 'exception',
    ),
)


def _parse_qs(url):
    if '?' not in url:
        return None, None, None

    url, qs = url.split('?')
    parsed = parse_qs(qs, keep_blank_values=True)
    ordering = None
    select = None
    query = None

    for k in parsed.keys():
        if k.startswith('ordering('):
            ordering = k[9:-1].split(',')
        elif k.startswith('select('):
            select = k[7:-1].split(',')
        else:
            value = parsed[k]
            if not value[0]:
                query = k

    return query, ordering, select


@pytest.fixture
def response():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def progress(mocker):
    return mocker.MagicMock()


@pytest.fixture
def response_factory():
    def _create_response(
        count=None,
        query=None,
        ordering=None,
        select=None,
        value=None,
        status=None,
        exception=None,
    ):
        return ConnectResponse(
            count=count,
            query=query,
            ordering=ordering,
            select=select,
            value=value,
            status=status,
            exception=exception,
        )
    return _create_response


@pytest.fixture
def client_factory():
    def _create_client(connect_responses):
        response_iterator = iter(connect_responses)

        def _execute_http_call(self, method, url, kwargs):
            res = next(response_iterator)

            query, ordering, select = _parse_qs(url)
            if res.query:
                assert query == res.query, 'RQL query does not match.'
            if res.ordering:
                assert ordering == res.ordering, 'RQL ordering does not match.'
            if res.select:
                assert select == res.select, 'RQL select does not match.'

            mock_kwargs = {
                'match_querystring': False,
            }
            if res.count is not None:
                end = 0 if res.count == 0 else res.count - 1
                mock_kwargs['status'] = 200
                mock_kwargs['headers'] = {'Content-Range': f'items 0-{end}/{res.count}'}
                mock_kwargs['json'] = []

            if isinstance(res.value, Iterable):
                count = len(res.value)
                end = 0 if count == 0 else count - 1
                mock_kwargs['status'] = 200
                mock_kwargs['json'] = res.value
                mock_kwargs['headers'] = {
                    'Content-Range': f'items 0-{end}/{count}',
                }
            elif isinstance(res.value, dict):
                mock_kwargs['status'] = res.status or 200
                mock_kwargs['json'] = res.value
            elif res.value is None:
                if res.exception:
                    mock_kwargs['body'] = res.exception
                else:
                    mock_kwargs['status'] = res.status or 200
            else:
                mock_kwargs['status'] = res.status or 200
                mock_kwargs['body'] = str(res.value)

            with responses.RequestsMock() as rsps:
                rsps.add(
                    method.upper(),
                    url,
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
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'ff_request.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def billing_request():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'billing_request.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def tcr_request():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'tcr_request.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def listing_request():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'listing_request.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def mkp_list():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'mkp_list.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def ta_list():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'ta_list.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def tier_account():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'ta_account.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def contract_response():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'contract_response.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def usage_records_response():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'usage_records_response.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def catalog_response():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'catalog.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def sla_response():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'sla_response.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def account_response():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'account.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def service_agreement_response():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'service_agreement.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def executive_fullfilment_requests_response():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'executive_fullfilment_requests.json',
        ),
    ) as request:
        return json.load(request)


@pytest.fixture
def helpdesk_response():
    with open(
        os.path.join(
            os.getcwd(),
            'tests',
            'fixtures',
            'helpdesk.json',
        ),
    ) as request:
        return json.load(request)
