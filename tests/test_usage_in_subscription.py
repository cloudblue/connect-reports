# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

import datetime

from reports.usage_in_subscription import entrypoint

from unittest.mock import patch


def test_generate_usage(
        progress,
        client_factory,
        response_factory,
        usage_records_response,
        ff_request,
):

    responses = []

    asset = ff_request['asset']

    parameters = {
        "period": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00",
        },
        "product": {
            "all": False,
            "choices": ["PRD-1"],
        },
    }

    responses.append(
        response_factory(
            count=1,
        ),
    )

    responses.append(
        response_factory(
            query='and(eq(status,active),in(product.id,(PRD-1)))',
            value=[asset],
        ),
    )

    responses.append(
        response_factory(
            query='and(eq(asset.id,AS-1895-0864-1238),in(status,(approved,closed)),or(and(ge('
                  'start_date,2020-12-01T00:00:00),lt(start_date,2021-01-01T00:00:00)),'
                  'and(ge(end_date,2020-12-01T00:00:00),lt(end_date,'
                  '2021-01-01T00:00:00))))',
            value=[usage_records_response],
        ),
    )

    client = client_factory(responses)

    with patch(
        'reports.usage_in_subscription.entrypoint.get_record',
        return_value=[[1, 2, 3]],
    ):

        result = list(entrypoint.generate(client, parameters, progress))

        assert len(result) == 1
        for res in result:
            assert res != ''


def test_record(
    progress,
    client_factory,
    response_factory,
    usage_records_response,
    ff_request,
):
    responses = [
        response_factory(
            query='eq(asset.id,AS-1895-0864-1238),in(status,(approved,closed)),(and(ge('
                  'start_date,2020-12-01T00:00:00),lt(start_date,2021-01-01T00:00:00))|and(ge('
                  'end_date,2020-12-01T00:00:00),lt(end_date,2021-01-01T00:00:00)))',
            value=[usage_records_response],
        ),
    ]

    client = client_factory(responses)

    thread_progress = entrypoint.Progress(progress, 100)
    result = entrypoint.get_record(
        client,
        ff_request['asset'],
        '2020-12-01T00:00:00',
        '2021-01-01T00:00:00',
        thread_progress,
    )

    assert result == [
        'AS-1895-0864-1238',
        '1147660',
        'processing',
        datetime.datetime(2020, 11, 23, 14, 18, 17),
        datetime.datetime(2020, 11, 23, 14, 23),
        'TA-2483-1010-5646',
        'Mayer-Kerluke', '1149069',
        'TA-0-2347-9392-6524',
        'Connectdemos',
        '1',
        '-',
        '-',
        '-',
        'PA-425-033',
        'CB Demo Provider',
        'VA-392-495',
        'Adrian Inc Oct 12',
        'PRD-276-377-545',
        'My Product',
        'HB-0309-9389',
        'IMC DEMOS',
        1,
        'UF-2021-01-3453-7567',
    ]
