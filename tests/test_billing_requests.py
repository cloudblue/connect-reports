# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from reports.billing_requests import generate


def test_generate(progress, client_factory, response_factory, billing_request):
    responses = []

    parameters = {
        "date": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00"
        },
        "product": None,
        "mkp": None,
        "hub": None
    }
    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00))',
            value=[billing_request]
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 6


def test_generate_additional(progress, client_factory, response_factory, billing_request):
    responses = []

    parameters = {
        "date": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00"
        },
        "product": [
            "PRD-276-377-545"
        ],
        "mkp": ['MP-123'],
        "hub": ['HB-123']
    }
    responses.append(
        response_factory(
            count=1,
        )
    )

    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),'
                  'in(asset.product.id,(PRD-276-377-545)),in(asset.marketplace.id,(MP-123)),'
                  'in(asset.connection.hub.id,(HB-123)))',
            value=[billing_request],
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 6
