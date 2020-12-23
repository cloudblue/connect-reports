# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from reports.fulfillment_requests_failed import generate


def test_generate(progress, client_factory, response_factory, ff_request):
    responses = []

    parameters = {
        "date": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00"
        },
        "product": None,
        "connection_type": None,
        "rr_type": None,
    }
    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),eq(status,'
                  'failed))',
            value=[ff_request]
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    assert result[0][0] == ff_request['id']
    assert result[0][1] == ff_request['type']
    assert result[0][3] == ff_request['asset']['tiers']['customer']['id']
    assert result[0][4] == ff_request['asset']['tiers']['customer']['name']
    assert result[0][5] == ff_request['asset']['tiers']['customer']['external_id']
    assert result[0][6] == ff_request['asset']['connection']['provider']['id']
    assert result[0][7] == ff_request['asset']['connection']['provider']['name']
    assert result[0][8] == ff_request['asset']['connection']['vendor']['id']
    assert result[0][9] == ff_request['asset']['connection']['vendor']['name']
    assert result[0][10] == ff_request['asset']['product']['id']
    assert result[0][11] == ff_request['asset']['product']['name']
    assert result[0][12] == ff_request['asset']['id']
    assert result[0][13] == ff_request['asset']['external_id']
    assert result[0][14] == ff_request['asset']['connection']['type']
    assert result[0][15] == ff_request['asset']['connection']['hub']['id']
    assert result[0][16] == ff_request['asset']['connection']['hub']['name']
    assert result[0][17] == ff_request['status']
    assert result[0][18] == ff_request['reason']


def test_generate_additional(progress, client_factory, response_factory, ff_request):
    responses = []

    parameters = {
        "date": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00"
        },
        "product": [
            "PRD-276-377-545"
        ],
        "connection_type": ['production'],
        "rr_type": ['purchase'],
    }
    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query='and(ge(created,2020-12-01T00:00:00),le(created,2021-01-01T00:00:00),'
                  'in(asset.product.id,(PRD-276-377-545)),in(type,(purchase)),eq(status,failed),'
                  'in(asset.connection.type,(production)))',
            value=[ff_request]
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    assert result[0][0] == ff_request['id']
    assert result[0][1] == ff_request['type']
    assert result[0][3] == ff_request['asset']['tiers']['customer']['id']
    assert result[0][4] == ff_request['asset']['tiers']['customer']['name']
    assert result[0][5] == ff_request['asset']['tiers']['customer']['external_id']
    assert result[0][6] == ff_request['asset']['connection']['provider']['id']
    assert result[0][7] == ff_request['asset']['connection']['provider']['name']
    assert result[0][8] == ff_request['asset']['connection']['vendor']['id']
    assert result[0][9] == ff_request['asset']['connection']['vendor']['name']
    assert result[0][10] == ff_request['asset']['product']['id']
    assert result[0][11] == ff_request['asset']['product']['name']
    assert result[0][12] == ff_request['asset']['id']
    assert result[0][13] == ff_request['asset']['external_id']
    assert result[0][14] == ff_request['asset']['connection']['type']
    assert result[0][15] == ff_request['asset']['connection']['hub']['id']
    assert result[0][16] == ff_request['asset']['connection']['hub']['name']
    assert result[0][17] == ff_request['status']
    assert result[0][18] == ff_request['reason']
