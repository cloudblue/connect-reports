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
        "tier_type": None,
        "full_contact_info": "no",
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
            query="and(ge(events.created.at,2020-12-01T00:00:00),le(events.created.at,"
                  "2021-01-01T00:00:00))",
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
    i = 0
    for res in result[0]:
        if res == '-':
            i += 1
    assert i == 10
    assert len(result[0]) == 20
