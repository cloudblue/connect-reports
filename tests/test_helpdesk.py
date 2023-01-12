# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue
# All rights reserved.
#

from reports.helpdesk.entrypoint import (
    generate,
    HEADERS,
)

PARAMETERS = {
    'date': {
        'after': '2020-12-01T00:00:00',
        'before': '2021-01-01T00:00:00',
    },
    'ticket_status': {
        'all': True,
        'choices': [],
    },
}


def test_generate(progress, client_factory, response_factory, helpdesk_response):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),'
                  'le(events.created.at,2021-01-01T00:00:00))',
            value=[helpdesk_response],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress))

    assert len(result) == 1


def test_generate_additional(progress, client_factory, response_factory, helpdesk_response):
    responses = []

    parameters = {
        'date': {
            'after': '2020-12-01T00:00:00',
            'before': '2021-01-01T00:00:00',
        },
        'ticket_status': {
            'all': False,
            'choices': ['pending'],
        },
    }
    responses.append(
        response_factory(
            count=1,
        ),
    )

    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),'
                  'le(events.created.at,2021-01-01T00:00:00),in(state,(pending)))',
            value=[helpdesk_response],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1


def test_generate_csv_renderer(progress, client_factory, response_factory, helpdesk_response):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),'
                  'le(events.created.at,2021-01-01T00:00:00))',
            value=[helpdesk_response],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='csv'))

    assert len(result) == 2
    assert result[0] == HEADERS
    assert len(result[0]) == 13
    assert result[0][0] == 'Case ID'
    assert progress.call_count == 2
    assert progress.call_args == ((2, 2),)


def test_generate_json_renderer(progress, client_factory, response_factory, helpdesk_response):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),'
                  'le(events.created.at,2021-01-01T00:00:00))',
            value=[helpdesk_response],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='json'))

    assert len(result) == 1
    assert len(result[0]) == 13
    assert result[0]['case_id'] == 'CA-925-402-166'
    assert progress.call_count == 1
    assert progress.call_args == ((1, 1),)
