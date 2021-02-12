# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from reports.listing_requests.entrypoint import generate


def test_generate(progress, client_factory, response_factory, listing_request):
    responses = []

    parameters = {
        "product": {
            "all": True,
            "choices": [],
        },
        "mkp": {
            "all": True,
            "choices": [],
        },
        "rr_status": {
            "all": True,
            "choices": [],
        },
    }
    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query='in(state,(draft,reviewing,deploying,completed,canceled))',
            value=[listing_request]
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    for res in result:
        assert res != "-"
        assert res is not None


def test_generate_all_params(progress, client_factory, response_factory, listing_request):
    responses = []

    parameters = {
        "date": {
            "value": {
                "after": "2020-12-01T00:00:00",
                "before": "2021-01-01T00:00:00",
            }
        },
        "product": {
            "all": False,
            "choices": ["PRD-123"],
        },
        "mkp": {
            "all": False,
            "choices": ["MKP-123"],
        },
        "rr_status": {
            "all": False,
            "choices": ["reviewing"],
        }
    }
    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),'
                  'in(listing.product.id,(PRD-123)),in(listing.contract.marketplace.id,(MKP-123)),'
                  'in(state,(reviewing)))',
            value=[listing_request]
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    for res in result:
        assert res != "-"
        assert res is not None
