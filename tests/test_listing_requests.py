# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from reports.listing_requests.entrypoint import generate


def test_generate(progress, client_factory, response_factory, listing_request):
    responses = []

    parameters = {
        "date": None,
        "product": None,
        "mkp": None,
        "rr_status": None,
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
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00"
        },
        "product": ["PRD-123"],
        "mkp": ["MKP-123"],
        "rr_status": ["reviewing"],
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