# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from reports.tier_configuration_requests.entrypoint import generate, HEADERS

PARAMETERS = {
    'date': {
        'after': '2020-12-01T00:00:00',
        'before': '2021-01-01T00:00:00',
    },
    'product': {
        'all': True,
        'choices': [],
    },
    'rr_type': {
        'all': True,
        'choices': [],
    },
    'rr_status': {
        'all': True,
        'choices': [],
    },
    'mkp': {
        'all': True,
        'choices': [],
    },
}


def test_generate(progress, client_factory, response_factory, tcr_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),le(events.created.at,'
                  '2021-01-01T00:00:00),in(status,(tiers_setup,inquiring,pending,approved,'
                  'failed)))',
            value=[tcr_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress))

    assert len(result) == 1
    for res in result:
        assert res != ''


def test_generate_all_params(progress, client_factory, response_factory, tcr_request):

    responses = []

    parameters = {
        'date': {
            'after': '2020-12-01T00:00:00',
            'before': '2021-01-01T00:00:00',
        },
        'product': {
            'all': False,
            'choices': ['PRD-1'],
        },
        'rr_type': {
            'all': False,
            'choices': ['setup'],
        },
        'rr_status': {
            'all': False,
            'choices': ['pending'],
        },
        'mkp': {
            'all': False,
            'choices': ['MKP-1'],
        },
    }

    responses.append(
        response_factory(
            count=1,
        ),
    )

    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),le(events.created.at,'
                  '2021-01-01T00:00:00),in(product.id,(PRD-1)),in(marketplace.id,(MKP-1)),'
                  'in(type,(setup)),in(status,(pending)))',
            value=[tcr_request],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    for res in result:
        assert res != ''


def test_generate_csv_renderer(progress, client_factory, response_factory, tcr_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),le(events.created.at,'
                  '2021-01-01T00:00:00),in(status,(tiers_setup,inquiring,pending,approved,'
                  'failed)))',
            value=[tcr_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='csv'))

    assert len(result) == 2
    assert result[0] == HEADERS
    assert len(result[0]) == 28
    assert result[0][0] == 'Request ID'
    assert progress.call_count == 2
    assert progress.call_args == ((2, 2),)


def test_generate_json_renderer(progress, client_factory, response_factory, tcr_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),le(events.created.at,'
                  '2021-01-01T00:00:00),in(status,(tiers_setup,inquiring,pending,approved,'
                  'failed)))',
            value=[tcr_request],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='json'))

    assert len(result) == 1
    assert len(result[0]) == 28
    assert result[0]['request_id'] == 'TCR-228-098-338-001'
    assert progress.call_count == 1
    assert progress.call_args == ((1, 1),)
