# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from reports.fulfillment_requests_line_item.entrypoint import (
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
    'rr_status': {
        'all': True,
        'choices': [],
    },
    'rr_type': {
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


def test_generate(progress, client_factory, response_factory, ff_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),in(status,'
                  '(tiers_setup,inquiring,pending,approved,failed)))',
            value=[ff_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress))

    assert len(result) == 18


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
        'rr_status': {
            'all': False,
            'choices': ['approved'],
        },
        'rr_type': {
            'all': False,
            'choices': ['purchase'],
        },
        'mkp': {
            'all': False,
            'choices': ['MP-123'],
        },
        'hub': {
            'all': False,
            'choices': ['HB-123'],
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
                  'in(asset.product.id,(PRD-276-377-545)),in(type,(purchase)),in(status,'
                  '(approved)),in(asset.marketplace.id,(MP-123)),in(asset.connection.hub.id,'
                  '(HB-123)))',
            value=[ff_request],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 18


def test_generate_csv_renderer(progress, client_factory, response_factory, ff_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),in(status,'
                  '(tiers_setup,inquiring,pending,approved,failed)))',
            value=[ff_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='csv'))

    assert len(result) == 19
    assert result[0] == HEADERS
    assert len(result[0]) == 34
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
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),in(status,'
                  '(tiers_setup,inquiring,pending,approved,failed)))',
            value=[ff_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='json'))

    assert len(result) == 18
    assert len(result[0]) == 34
    assert result[0]['request_id'] == 'PR-1895-0864-1238-001'
    assert progress.call_count == 1
    assert progress.call_args == ((1, 1),)
