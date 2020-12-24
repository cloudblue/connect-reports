# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from reports.subscription_list.entrypoint import (
    generate,
    calculate_period,
    get_anniversary_day,
    get_anniversary_month,
)


def test_generate(progress, client_factory, response_factory, billing_request):
    responses = []

    parameters = {
        "date": None,
        "product": None,
        "mkp": None,
        "period": None,
        "status": None
    }

    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query=None,
            value=[billing_request['asset']]
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1


def test_generate_all_params(progress, client_factory, response_factory, billing_request):
    responses = []

    parameters = {
        "date": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00"
        },
        "product": [
            "PRD-276-377-545"
        ],
        "mkp": ["MP-123"],
        "period": ["monthly"],
        "status": ["active"]
    }

    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query=None,
            value=[billing_request['asset']]
        )
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
        }
    }
    assert 2 == get_anniversary_day(subscription)
    assert "-" == get_anniversary_month(subscription)
    subscription['anniversary']['month'] = 2
    assert 2 == get_anniversary_month(subscription)
