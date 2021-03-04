# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from cnct import R

from reports.utils import convert_to_datetime, get_basic_value, get_value


def generate(client, parameters, progress_callback):
    query = R()
    if parameters.get('type') and parameters['type']['all'] is False:
        query &= R().type.oneof(parameters['type']['choices'])
    if parameters.get('status') and parameters['status']['all'] is False:
        query &= R().status.oneof(parameters['status']['choices'])
    contracts = client.contracts.filter(query).select("agreement").order_by("-status")
    progress = 0
    total = contracts.count()

    for contract in contracts:
        yield (
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
        progress += 1
        progress_callback(progress, total)
