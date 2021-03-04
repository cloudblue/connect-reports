# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from reports.fulfillment_requests_failed.entrypoint import generate


def test_generate(progress, client_factory, response_factory, ff_request):
    responses = []

    parameters = {
        "date": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00",
        },
        "product": {
            "all": True,
            "choices": [],
        },
        "connection_type": {
            "all": True,
            "choices": [],
        },
        "rr_type": {
            "all": True,
            "choices": [],
        },
    }
    responses.append(
        response_factory(
            count=1,
        ),
    )

    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),eq(status,'
                  'failed))',
            value=[ff_request],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1


def test_generate_additional(progress, client_factory, response_factory, ff_request):
    responses = []

    parameters = {
        "date": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00",
        },
        "product": {
            "all": False,
            "choices": [
                "PRD-276-377-545",
            ],
        },
        "connection_type": {
            "all": False,
            "choices": ['production'],
        },
        "rr_type": {
            "all": False,
            "choices": ['purchase'],
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
                  'in(asset.product.id,(PRD-276-377-545)),in(type,(purchase)),eq(status,failed),'
                  'in(asset.connection.type,(production)))',
            value=[ff_request],
        ),
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
