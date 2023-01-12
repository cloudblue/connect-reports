# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue
# All rights reserved.
#

from reports.listing_requests.entrypoint import (
    generate,
    HEADERS,
)

PARAMETERS = {
    'product': {
        'all': True,
        'choices': [],
    },
    'mkp': {
        'all': True,
        'choices': [],
    },
    'rr_status': {
        'all': True,
        'choices': [],
    },
}


def test_generate(progress, client_factory, response_factory, listing_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='in(state,(draft,reviewing,deploying,completed,canceled))',
            value=[listing_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress))

    assert len(result) == 1
    for res in result:
        assert res != '-'
        assert res is not None


def test_generate_all_params(progress, client_factory, response_factory, listing_request):
    responses = []

    parameters = {
        'date': {
            'after': '2020-12-01T00:00:00',
            'before': '2021-01-01T00:00:00',
        },
        'product': {
            'all': False,
            'choices': ['PRD-123'],
        },
        'mkp': {
            'all': False,
            'choices': ['MKP-123'],
        },
        'rr_status': {
            'all': False,
            'choices': ['reviewing'],
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
                  'in(listing.product.id,(PRD-123)),in(listing.contract.marketplace.id,(MKP-123)),'
                  'in(state,(reviewing)))',
            value=[listing_request],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    for res in result:
        assert res != '-'
        assert res is not None


def test_generate_csv_renderer(progress, client_factory, response_factory, listing_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='in(state,(draft,reviewing,deploying,completed,canceled))',
            value=[listing_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='csv'))

    assert len(result) == 2
    assert result[0] == HEADERS
    assert len(result[0]) == 14
    assert result[0][0] == 'Request ID'
    assert progress.call_count == 2
    assert progress.call_args == ((2, 2),)


def test_generate_json_renderer(progress, client_factory, response_factory, listing_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='in(state,(draft,reviewing,deploying,completed,canceled))',
            value=[listing_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='json'))

    assert len(result) == 1
    assert len(result[0]) == 14
    assert result[0]['request_id'] == 'LSTR-316-530-321-001'
    assert progress.call_count == 1
    assert progress.call_args == ((1, 1),)
