# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue
# All rights reserved.
#

from reports.fulfillment_requests_failed.entrypoint import (
    generate,
    HEADERS,
)

PARAMETERS = {
    'date': {
        'after': '2020-12-01T00:00:00',
        'before': '2021-01-01T00:00:00',
    },
    'product': {
        'all': True,
        'choices': [],
    },
    'connection_type': {
        'all': True,
        'choices': [],
    },
    'rr_type': {
        'all': True,
        'choices': [],
    },
}


def test_generate(progress, client_factory, response_factory, ff_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),eq(status,'
                  'failed))',
            value=[ff_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress))

    assert len(result) == 1


def test_generate_additional(progress, client_factory, response_factory, ff_request):
    responses = []

    parameters = {
        'date': {
            'after': '2020-12-01T00:00:00',
            'before': '2021-01-01T00:00:00',
        },
        'product': {
            'all': False,
            'choices': [
                'PRD-276-377-545',
            ],
        },
        'connection_type': {
            'all': False,
            'choices': ['production'],
        },
        'rr_type': {
            'all': False,
            'choices': ['purchase'],
        },
    }
    responses.append(
        response_factory(
            count=1,
        ),
    )

    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),'
                  'in(asset.product.id,(PRD-276-377-545)),in(type,(purchase)),eq(status,failed),'
                  'in(asset.connection.type,(production)))',
            value=[ff_request],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1


def test_generate_csv_renderer(progress, client_factory, response_factory, ff_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),eq(status,'
                  'failed))',
            value=[ff_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='csv'))

    assert len(result) == 2
    assert result[0] == HEADERS
    assert len(result[0]) == 27
    assert result[0][0] == 'Request ID'
    assert progress.call_count == 2
    assert progress.call_args == ((2, 2),)


def test_generate_json_renderer(progress, client_factory, response_factory, ff_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),eq(status,'
                  'failed))',
            value=[ff_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='json'))

    assert len(result) == 1
    assert len(result[0]) == 27
    assert result[0]['request_id'] == 'PR-1895-0864-1238-001'
    assert progress.call_count == 1
    assert progress.call_args == ((1, 1),)
