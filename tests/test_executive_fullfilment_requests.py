from copy import deepcopy
from datetime import datetime

import reports
from reports.executive_fullfilment_requests.entrypoint import (
    _generate_bar_charts_from_data,
    _get_request_count_group_by_type,
    _get_requests,
    generate,
    Part,
)


def test_get_requests(
    mocker,
):
    parameters = {
        'date': {
            'after': '2020-11-23T14:18:17+00:00',
            'before': '2020-11-24T14:18:17+00:00',
        },
        'product': {'all': False, 'choices': ['PRD-1']},
        'rr_type': {'all': False, 'choices': ['purchase']},
    }

    fake_client = mocker.MagicMock()
    fake_filter = mocker.MagicMock()
    fake_client.requests = mocker.MagicMock(return_value=fake_filter)
    _get_requests(fake_client, parameters)
    expected_filter = (
        f'and(ge(created,{parameters["date"]["after"]}),le(created,{parameters["date"]["before"]}),'
    )
    expected_filter += (
        'in(status,(approved,failed,revoked)),in(asset.product.id,(PRD-1)),in(type,(purchase)))'
    )
    assert str(fake_client.requests.filter.call_args_list[0][0][0]) == expected_filter


def test_get_request_count_group_by_type(
    mocker,
):

    parameters = {
        'date': {
            'after': '2020-11-23T14:18:17+00:00',
            'before': '2020-11-24T14:18:17+00:00',
        },
        'product': {'all': False, 'choices': ['PRD-1']},
    }
    fake_client = mocker.MagicMock()
    fake_filter = mocker.MagicMock()
    fake_filter.count = mocker.MagicMock()
    fake_client.requests = mocker.MagicMock(return_value=fake_filter)

    for rr_type in ('adjustment', 'purchase', 'change', 'suspend', 'resume', 'cancel'):
        parameters['rr_type'] = {'all': False, 'choices': [rr_type]}
        _get_request_count_group_by_type(fake_client, parameters)

    call_number = 0
    for rr_type in ('adjustment', 'purchase', 'change', 'suspend', 'resume', 'cancel'):
        expected_filter = (
            f'and(ge(created,{parameters["date"]["after"]}),le(created,'
            f'{parameters["date"]["before"]}),'
        )
        expected_filter += (
            f'in(status,(approved,failed,revoked)),in(asset.product.id,(PRD-1)),eq(type,{rr_type}))'
        )
        assert str(fake_client.requests.filter.call_args_list[call_number][0][0]) == expected_filter
        call_number += 2


def test_generate(
    progress,
    client_factory,
    response_factory,
    account_response,
    executive_fullfilment_requests_response,
    mocker,
    monkeypatch,
):
    class MyDatetimeClass():
        def today():
            return datetime(year=2021, month=8, day=23)

    monkeypatch.setattr(reports.executive_fullfilment_requests.entrypoint, 'date', MyDatetimeClass)

    mocker.patch(
        'connect.client.models.resourceset.ResourceSet.count',
        return_value=7,
    )

    responses = []

    own_executive_fullfilment_requests_response = deepcopy(executive_fullfilment_requests_response)
    responses.append(
        response_factory(
            value=own_executive_fullfilment_requests_response,
        ),
    )
    responses.append(
        response_factory(
            value=[account_response],
        ),
    )

    client = client_factory(responses)
    parameters = {
        'date': {
            'after': '2020-11-23T14:18:17+00:00',
            'before': '2020-11-24T14:18:17+00:00',
        },
    }
    result = generate(
        client,
        parameters,
        progress,
        renderer_type='pdf',
        extra_context=mocker.MagicMock(),
    )

    assert len(result) == 3
    assert result['generation_date'] == 'August 23, 2021'
    assert result['range'] == {
        'start': '2020-11-23',
        'end': '2020-11-24',
    }

    assert result['charts'][0]['title'] == '1. Distribution of requests per type'
    assert result['charts'][0]['description'] == (
        'Total amount of requests within the period from 2020-11-23 to 2020-11-24 : <b>7<b>.'
    )
    assert len(result['charts'][0]['images']) == 1

    assert result['charts'][1]['title'] == '2. Requests per country'
    assert result['charts'][1]['description'] == (
        'Following charts represents the request amount per country. The countries that have more '
        'than the 20% are near red.'
    )
    assert len(result['charts'][1]['table']) == 6
    assert len(result['charts'][1]['images']) == 1

    assert result['charts'][2]['title'] == '3. Requests per product per type'
    assert result['charts'][2]['description'] == (
        'Following charts represents the request amount per product. Bar contains the distribution '
        'of requests per type.'
    )
    assert len(result['charts'][2]['images']) == 1

    assert result['charts'][3]['title'] == '4. Averge Request Processing time (per vendor)'
    assert result['charts'][3]['description'] == (
        'Following charts represents the average processing time of requests per vendor.'
    )
    assert len(result['charts'][3]['images']) == 1

    assert result['charts'][4]['title'] == '5. Averge Request Processing time (per product)'
    assert result['charts'][4]['description'] == (
        'Following charts represents the average processing time of requests per product. Bar '
        'contains the distribution of requests per type.'
    )
    assert len(result['charts'][4]['images']) == 1


def test_generate_bar_charts_from_data_threshold(
    mocker,
):

    mocker.patch(
        'reports.executive_fullfilment_requests.entrypoint._calculate_the_average_and_sort',
        return_value={
            '1': {'name': '1', 'avg': 0.5},
            '2': {'name': '2', 'avg': 0.1},
            '3': {'name': '3', 'avg': 0.04},
        },
    )
    mocked_split_chart_data = mocker.patch(
        'reports.executive_fullfilment_requests.entrypoint._split_chart_data',
        return_value=[Part(0, 2, 1, 1)],
    )
    _generate_bar_charts_from_data(mocker.MagicMock(), 'Vendor')
    mocked_split_chart_data.assert_called_with(2)
