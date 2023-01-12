# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue
# All rights reserved.
#

import datetime

from reports.usage_in_subscription import entrypoint

from unittest.mock import patch

PARAMETERS = {
    'period': {
        'after': '2020-12-01T00:00:00',
        'before': '2021-01-01T00:00:00',
    },
    'product': {
        'all': False,
        'choices': ['PRD-1'],
    },
}


def test_generate_usage(
        progress,
        client_factory,
        response_factory,
        usage_records_response,
        ff_request,
):
    responses = []
    asset = ff_request['asset']
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
        result = list(entrypoint.generate(client, PARAMETERS, progress))

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

    assert result == (
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
    )


def test_json_record(
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
        'json',
    )

    assert result == {
        'asset_id': 'AS-1895-0864-1238',
        'asset_external_id': '1147660',
        'asset_status': 'processing',
        'asset_created_at': datetime.datetime(2020, 11, 23, 14, 18, 17),
        'asset_updated_at': datetime.datetime(2020, 11, 23, 14, 23),
        'customer_id': 'TA-2483-1010-5646',
        'customer_name': 'Mayer-Kerluke',
        'customer_external_id': '1149069',
        'tier_1_id': 'TA-0-2347-9392-6524',
        'tier_1_name': 'Connectdemos',
        'tier_1_external_id': '1',
        'tier_2_id': '-',
        'tier_2_name': '-',
        'tier_2_external_id': '-',
        'provider_id': 'PA-425-033',
        'provider_name': 'CB Demo Provider',
        'vendor_id': 'VA-392-495',
        'vendor_name': 'Adrian Inc Oct 12',
        'product_id': 'PRD-276-377-545',
        'product_name': 'My Product',
        'hub_id': 'HB-0309-9389',
        'hub_name': 'IMC DEMOS',
        'usage_reports_count': 1,
        'usage_reports_ids': 'UF-2021-01-3453-7567',
    }


def test_generate_usage_csv_renderer(
        progress,
        client_factory,
        response_factory,
        usage_records_response,
        ff_request,
):
    responses = []
    asset = ff_request['asset']
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
        result = list(entrypoint.generate(client, PARAMETERS, progress, renderer_type='csv'))

        assert len(result) == 2
        assert result[0] == entrypoint.HEADERS
        assert len(result[0]) == 24
        assert result[0][0] == 'Asset ID'


def test_generate_usage_json_renderer(
        progress,
        client_factory,
        response_factory,
        usage_records_response,
        ff_request,
):
    responses = []
    asset = ff_request['asset']
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
        return_value={'key_1': 'value_1', 'key_2': 'value_2', 'key_3': 'value_3'},
    ):
        result = list(entrypoint.generate(client, PARAMETERS, progress, renderer_type='json'))
        assert len(result) == 1
        assert len(result[0]) == 3
        assert result[0]['key_1'] == 'value_1'
