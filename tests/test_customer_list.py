# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from reports.customers_list.entrypoint import generate


def test_generate(progress, client_factory, response_factory, mkp_list, ta_list, tier_account):

    responses = []

    parameters = {
        "date": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00",
        },
        "mkp": ["mkp-1"],
        "tier_type": ["mkp2"],
    }

    responses.append(
        response_factory(
            value=mkp_list
        )
    )

    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query="and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),"
                  "in(asset.marketplace.id,(mkp-1)),in(scopes,(mkp2)))",
            value=ta_list,
        )
    )

    responses.append(
        response_factory(
            value=tier_account,
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    assert '-' not in result[0]
    assert len(result[0]) == 22


def test_generate_2(progress, client_factory, response_factory, mkp_list, ta_list, tier_account):

    responses = []

    parameters = {
        "date": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00",
        },
        "mkp": None,
        "tier_type": None,
    }

    responses.append(
        response_factory(
            value=mkp_list
        )
    )

    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query="and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00))",
            value=ta_list
        )
    )

    responses.append(
        response_factory(
            value=tier_account
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    assert '-' not in result[0]
    assert len(result[0]) == 22
