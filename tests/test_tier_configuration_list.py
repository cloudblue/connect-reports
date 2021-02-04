# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from reports.tier_configuration_list.entrypoint import generate


def test_generate(progress, client_factory, response_factory, tcr_request):

    responses = []

    parameters = {
        "product": {
            "all": True,
            "choices": [],
        },
        "rr_status": {
            "all": True,
            "choices": [],
        },
        "mkp": {
            "all": True,
            "choices": [],
        }
    }

    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query='in(status,(active,processing))',
            value=[tcr_request['configuration']]
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    for res in result:
        assert res != ''


def test_generate_all_params(progress, client_factory, response_factory, tcr_request):

    responses = []

    parameters = {
        "date": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00"
        },
        "product": {
            "all": False,
            "choices": ["PRD-1"],
        },
        "rr_type": {
            "all": False,
            "choices": ["setup"],
        },
        "rr_status": {
            "all": False,
            "choices": ['pending'],
        },
        "mkp": {
            "all": False,
            "choices": ["MKP-1"],
        },
    }

    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query='and(ge(events.created.at,2020-12-01T00:00:00),le(events.created.at,'
                  '2021-01-01T00:00:00),in(product.id,(PRD-1)),in(marketplace.id,(MKP-1)),'
                  'in(status,(pending)))',
            value=[tcr_request['configuration']]
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    for res in result:
        assert res != ''
