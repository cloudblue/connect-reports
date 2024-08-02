# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue
# All rights reserved.
#
import copy

import pytest

from reports.customers_list.entrypoint import (
    generate,
    HEADERS,
)

PARAMETERS = {
    'date': {
        'after': '2020-12-01T00:00:00',
        'before': '2021-01-01T00:00:00',
    },
    'tier_type': None,
}


@pytest.mark.parametrize(
    'parameter_choices,expected_rql',
    (
        ({'choices': ['customer']}, ',eq(type,customer)'),
        ({'choices': ['tier1']}, ',eq(type,reseller)'),
        ({'choices': ['tier2']}, ',eq(type,reseller)'),
        ({'choices': ['tier2', 'tier1']}, ',eq(type,reseller)'),
        ({'choices': ['customer', 'tier1']}, ''),
        ({'choices': ['customer', 'tier2']}, ''),
        ({'choices': ['customer', 'tier1', 'tier1', 'tier2']}, ''),

    ),
)
def test_generate(
    progress,
    client_factory,
    response_factory,
    mkp_list,
    ta_list,
    tier_account,
    parameter_choices,
    expected_rql,
):
    parameters = copy.deepcopy(PARAMETERS)
    parameters['tier_type'] = {**parameter_choices, 'all': False}
    responses = []
    responses.append(
        response_factory(
            value=mkp_list,
        ),
    )
    responses.append(
        response_factory(
            count=1,
        ),
    )
    ta_list_query = (
        'and(ge(events.created.at,2020-12-01T00:00:00),le(events.created.at,'
        '2021-01-01T00:00:00){0})'
    )
    responses.append(
        response_factory(
            query=ta_list_query.format(expected_rql),
            value=ta_list,
        ),
    )
    responses.append(
        response_factory(
            value=tier_account,
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    i = 0
    for res in result[0]:
        if res == '-':
            i += 1
    assert i == 3
    assert len(result[0]) == 20


def test_generate_csv_renderer(
    progress,
    client_factory,
    response_factory,
    mkp_list,
    ta_list,
    tier_account,
):
    responses = []
    responses.append(
        response_factory(
            value=mkp_list,
        ),
    )
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),le(events.created.at,'
                  '2021-01-01T00:00:00))',
            value=ta_list,
        ),
    )
    responses.append(
        response_factory(
            value=tier_account,
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='csv'))

    assert len(result) == 2
    assert result[0] == HEADERS
    assert len(result[0]) == 20
    assert result[0][0] == 'Account ID'
    assert progress.call_count == 2
    assert progress.call_args == ((2, 2),)


def test_generate_json_renderer(
    progress,
    client_factory,
    response_factory,
    mkp_list,
    ta_list,
    tier_account,
):
    responses = []
    responses.append(
        response_factory(
            value=mkp_list,
        ),
    )
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),le(events.created.at,'
                  '2021-01-01T00:00:00))',
            value=ta_list,
        ),
    )
    responses.append(
        response_factory(
            value=tier_account,
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='json'))

    assert len(result) == 1
    assert len(result[0]) == 20
    assert result[0]['account_id'] == 'TA-6487-8891-3817'
    assert progress.call_count == 1
    assert progress.call_args == ((1, 1),)
