# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue
# All rights reserved.
#

from reports.contract_list.entrypoint import (
    generate,
    HEADERS,
)

PARAMETERS = {
    'type': {
        'all': True,
        'choices': [],
    },
    'status': {
        'all': True,
        'choice': [],
    },
}


def test_generate(progress, client_factory, response_factory, contract_response):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            value=[contract_response],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress))

    assert len(result) == 1
    for res in result:
        assert res != '-'
        assert res is not None


def test_generate_all_params(progress, client_factory, response_factory, contract_response):
    responses = []

    parameters = {
        'type': {
            'all': False,
            'choices': ['distribution'],
        },
        'status': {
            'all': False,
            'choices': ['active'],
        },
    }
    responses.append(
        response_factory(
            count=1,
        ),
    )

    responses.append(
        response_factory(
            query='and(in(type,(distribution)),in(status,(active)))',
            value=[contract_response],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    for res in result:
        assert res != '-'
        assert res is not None


def test_generate_csv_renderer(progress, client_factory, response_factory, contract_response):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            value=[contract_response],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='csv'))

    assert result[0] == HEADERS
    assert len(result[0]) == 16
    assert result[0][0] == 'Contract ID'
    assert len(result) == 2
    assert progress.call_count == 2
    assert progress.call_args == ((2, 2),)


def test_generate_json_renderer(progress, client_factory, response_factory, contract_response):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            value=[contract_response],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='json'))

    assert len(result) == 1
    assert len(result[0]) == 16
    assert result[0]['contract_id'] == 'CRD-58096-38285-80856'
    assert progress.call_count == 1
    assert progress.call_args == ((1, 1),)
