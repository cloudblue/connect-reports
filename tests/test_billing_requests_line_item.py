# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue
# All rights reserved.
#

from reports.billing_requests_line_item.entrypoint import (
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
    'mkp': {
        'all': True,
        'choices': [],
    },
    'hub': {
        'all': True,
        'choices': [],
    },
}


def test_generate(progress, client_factory, response_factory, billing_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00))',
            value=[billing_request],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, PARAMETERS, progress))

    assert len(result) == 6


def test_generate_additional(progress, client_factory, response_factory, billing_request):
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
        'mkp': {
            'all': False,
            'choices': [
                'MP-123',
            ],
        },
        'hub': {
            'all': False,
            'choices': [
                'HB-123',
            ],
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
                  'in(asset.product.id,(PRD-276-377-545)),in(asset.marketplace.id,(MP-123)),'
                  'in(asset.connection.hub.id,(HB-123)))',
            value=[billing_request],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 6


def test_generate_csv_renderer(progress, client_factory, response_factory, billing_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00))',
            value=[billing_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='csv'))

    assert len(result) == 7
    assert result[0] == HEADERS
    assert len(result[0]) == 34
    assert result[0][0] == 'Billing request ID'
    assert result[1][0] == 'BRV-3970-9735-4579-0002'
    assert progress.call_count == 2
    assert progress.call_args == ((2, 2),)


def test_generate_json_renderer(progress, client_factory, response_factory, billing_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00))',
            value=[billing_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='json'))

    assert len(result) == 6
    assert len(result[0].items()) == 34
    assert result[0]['billing_request_id'] == 'BRV-3970-9735-4579-0002'
    assert progress.call_count == 1
    assert progress.call_args == ((1, 1),)
