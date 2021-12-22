# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from reports.subscription_list.entrypoint import (
    calculate_period,
    generate,
    get_anniversary_day,
    get_anniversary_month,
    HEADERS,
)

from copy import deepcopy

PARAMETERS = {
    'date': None,
    'product': {
        'all': True,
        'choices': [],
    },
    'mkp': {
        'all': True,
        'choices': [],
    },
    'period': {
        'all': True,
        'choices': [],
    },
    'status': {
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
            query=None,
            value=[billing_request['asset']],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress))

    assert len(result) == 1


def test_generate_all_params(progress, client_factory, response_factory, billing_request):
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
            'choices': ['MP-123'],
        },
        'period': {
            'all': False,
            'choices': ['monthly'],
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
            query=None,
            value=[billing_request['asset']],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1


def test_calculate_period():
    assert 'Monthly' == calculate_period(1, 'monthly')
    assert 'Yearly' == calculate_period(1, 'yearly')
    assert '2 Months' == calculate_period(2, 'monthly')
    assert '2 Years' == calculate_period(2, 'yearly')


def test_get_anniversaries():
    assert '-' == get_anniversary_day({})
    subscription = {
        'anniversary': {
            'day': 2,
        },
    }
    assert 2 == get_anniversary_day(subscription)
    assert '-' == get_anniversary_month(subscription)
    subscription['anniversary']['month'] = 2
    assert 2 == get_anniversary_month(subscription)


def test_generate_csv_renderer(progress, client_factory, response_factory, billing_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    responses.append(
        response_factory(
            query=None,
            value=[billing_request['asset']],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='csv'))

    assert len(result) == 2
    assert result[0] == HEADERS
    assert len(result[0]) == 29
    assert result[0][0] == 'Subscription ID'
    assert progress.call_count == 2
    assert progress.call_args == ((2, 2),)


def test_generate_json_renderer(progress, client_factory, response_factory, billing_request):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )
    asset1 = deepcopy(billing_request['asset'])
    asset2 = deepcopy(billing_request['asset'])
    asset2['id'] = 'AS-123'
    asset2['product']['id'] = 'PRD-2'
    responses.append(
        response_factory(
            query=None,
            value=[asset1, asset2],
        ),
    )
    param_asset2 = {
        'id': '1',
        'name': 't0_f_text',
        'constraints': {
            'reconciliation': True,
        },
    }
    responses.append(
        response_factory(
            value=[],
        ),
    )
    responses.append(
        response_factory(
            value=[param_asset2],
        ),
    )
    client = client_factory(responses)
    result = list(generate(client, PARAMETERS, progress, renderer_type='json'))

    assert len(result) == 2
    assert len(result[0]) == 29
    assert result[0]['subscription_id'] == 'AS-3970-9735-4579'
    assert result[0]['vendor_primary_key'] == '-'
    assert result[1]['subscription_id'] == 'AS-123'
    assert result[1]['vendor_primary_key'] == 't'
    assert progress.call_count == 2
