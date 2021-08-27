from datetime import datetime

import reports
from reports.sla.entrypoint import generate
from reports.utils import convert_to_datetime, get_dict_element


PARAMETERS = {
    'offset_red': 5,
    'offset_yellow': 2,
}


FAKE_DATE = datetime(year=2021, month=8, day=23)


def _get_sla_group(created):
    days = (FAKE_DATE - created).days
    if days >= PARAMETERS['offset_red']:
        return 'RED'
    elif days >= PARAMETERS['offset_yellow']:
        return 'YELLOW'
    else:
        return 'GREEN'


def _concat_if_content(text1, text2):
    if text1 and text2:
        return f'{text1} {text2}'
    return ''


def test_generate(
    progress,
    client_factory,
    response_factory,
    sla_response,
    mocker,
    monkeypatch,
):

    class MyDatetimeClass():
        def utcnow():
            return FAKE_DATE

    monkeypatch.setattr(reports.sla.entrypoint.datetime, 'datetime', MyDatetimeClass)

    mocker.patch(
        'connect.client.models.resourceset.ResourceSet.count',
        return_value=9,
    )

    responses = []
    responses.append(
        response_factory(
            value=sla_response,
        ),
    )

    client = client_factory(responses)

    parameters = {'offset_red_days': 5, 'offset_yellow_days': 2}
    generator = generate(
        client,
        parameters,
        progress,
        renderer_type='xlsx',
        extra_context_callback=mocker.MagicMock(),
    )
    expected = []
    for row in sla_response:
        days = (FAKE_DATE - convert_to_datetime(row['created'])).days
        sla_group = _get_sla_group(convert_to_datetime(row['created']))
        expected.append((
            row['id'],
            get_dict_element(row, 'asset', 'product', 'id'),
            get_dict_element(row, 'asset', 'product', 'name'),
            get_dict_element(row, 'asset', 'connection', 'vendor', 'id'),
            get_dict_element(row, 'asset', 'connection', 'vendor', 'name'),
            get_dict_element(row, 'asset', 'connection', 'provider', 'id'),
            get_dict_element(row, 'asset', 'connection', 'provider', 'name'),
            get_dict_element(row, 'type'),
            days,
            convert_to_datetime(get_dict_element(row, 'created')),
            get_dict_element(row, 'status'),
            get_dict_element(row, 'asset', 'connection', 'type'),
            get_dict_element(row, 'assignee', 'email'),
            get_dict_element(row, 'asset', 'tiers', 'customer', 'id'),
            get_dict_element(row, 'asset', 'tiers', 'customer', 'external_id'),
            get_dict_element(row, 'asset', 'tiers', 'customer', 'name'),
            _concat_if_content(
                get_dict_element(
                    row,
                    'asset',
                    'tiers',
                    'customer',
                    'contact_info',
                    'contact',
                    'last_name',
                ),
                get_dict_element(
                    row,
                    'asset',
                    'tiers',
                    'customer',
                    'contact_info',
                    'contact',
                    'first_name',
                ),
            ),
            get_dict_element(
                row,
                'asset',
                'tiers',
                'customer',
                'contact_info',
                'contact',
                'email',
            ),
            get_dict_element(row, 'asset', 'tiers', 'tier1', 'name'),
            get_dict_element(row, 'asset', 'tiers', 'tier1', 'external_id'),
            _concat_if_content(
                get_dict_element(
                    row,
                    'asset',
                    'tiers',
                    'tier1',
                    'contact_info',
                    'contact',
                    'last_name',
                ),
                get_dict_element(
                    row,
                    'asset',
                    'tiers',
                    'tier1',
                    'contact_info',
                    'contact',
                    'first_name',
                ),
            ),
            get_dict_element(
                row,
                'asset',
                'tiers',
                'tier1',
                'contact_info',
                'contact',
                'email',
            ),
            get_dict_element(row, 'asset', 'tiers', 'tier2', 'name'),
            get_dict_element(row, 'asset', 'tiers', 'tier2', 'external_id'),
            _concat_if_content(
                get_dict_element(
                    row,
                    'asset',
                    'tiers',
                    'tier2',
                    'contact_info',
                    'contact',
                    'last_name',
                ),
                get_dict_element(
                    row,
                    'asset',
                    'tiers',
                    'tier2',
                    'contact_info',
                    'contact',
                    'first_name',
                ),
            ),
            get_dict_element(
                row,
                'asset',
                'tiers',
                'tier2',
                'contact_info',
                'contact',
                'email',
            ),
            get_dict_element(row, 'marketplace', 'id'),
            get_dict_element(row, 'marketplace', 'name'),
            sla_group,
        ))

    index = 0
    items = list(generator)
    for element in items:
        assert element == expected[index]
        index += 1
