# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from connect.client import R

from reports.utils import convert_to_datetime, get_basic_value, get_value

HEADERS = (
    'Contract ID', 'Type', 'Version', 'Updates available',
    'Agreement ID', 'Agreement', 'Issuer', 'Creation Date',
    'Marketplace ID', 'MarketPlace', 'Product ID', 'Product',
    'Signee', 'Signature Date',
    'Counter Signee', 'Counter Signature Date',
)


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    contracts = _get_contracts(client, parameters)
    total = contracts.count()
    progress = 0
    if renderer_type == 'csv':
        yield HEADERS
        total += 1
        progress += 1
        progress_callback(progress, total)

    for contract in contracts:
        if renderer_type == 'json':
            yield {
                HEADERS[idx].replace(' ', '_').lower(): value
                for idx, value in enumerate(_process_line(contract))
            }
        else:
            yield _process_line(contract)
        progress += 1
        progress_callback(progress, total)


def _get_contracts(client, parameters):
    query = R()

    if parameters.get('type') and parameters['type']['all'] is False:
        query &= R().type.oneof(parameters['type']['choices'])
    if parameters.get('status') and parameters['status']['all'] is False:
        query &= R().status.oneof(parameters['status']['choices'])

    return client.contracts.filter(query).select("agreement").order_by("-status")


def _process_line(contract):
    return (
        get_basic_value(contract, 'id'),
        get_basic_value(contract, 'type'),
        get_basic_value(contract, 'version'),
        'Yes' if get_basic_value(contract, 'latest') is False else '-',
        get_value(contract, 'agreement', 'id'),
        get_value(contract, 'agreement', 'name'),
        get_value(contract, 'issuer', 'name'),
        convert_to_datetime(get_value(contract['events'], 'created', 'at')),
        get_value(contract, 'marketplace', 'id'),
        get_value(contract, 'marketplace', 'name'),
        get_value(contract['sourcing'], 'product', 'id') if 'sourcing' in contract else '-',
        get_value(contract['sourcing'], 'product', 'name') if 'sourcing' in contract else '-',
        get_value(
            contract['events']['signed'],
            'by',
            'name',
        ) if 'signed' in contract['events'] else '-',
        convert_to_datetime(
            get_value(
                contract['events'],
                'signed',
                'at',
            ),
        ) if 'created' in contract['events'] else '-',
        get_value(
            contract['events']['countersigned'],
            'by',
            'name',
        ) if 'countersigned' in contract['events'] else '-',
        convert_to_datetime(
            get_value(
                contract['events'],
                'countersigned',
                'at',
            ),
        ) if 'countersigned' in contract['events'] else '-',
    )
