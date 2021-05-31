# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from connect.client import R

from reports.utils import convert_to_datetime, get_basic_value, get_value, today_str


def generate(client=None, parameters=None, progress_callback=None, renderer_type=None, extra_context_callback=None):
    requests = _get_requests(client, parameters)

    progress = 0
    total = requests.count()

    for request in requests:
        connection = request['asset']['connection']
        yield (
            get_basic_value(request, 'id'),
            get_basic_value(request, 'type'),
            convert_to_datetime(
                get_basic_value(request, 'created'),
            ),
            convert_to_datetime(
                get_basic_value(request, 'updated'),
            ),
            today_str(),
            get_value(request['asset']['tiers'], 'customer', 'id'),
            get_value(request['asset']['tiers'], 'customer', 'name'),
            get_value(request['asset']['tiers'], 'customer', 'external_id'),
            get_value(request['asset']['tiers'], 'tier1', 'id'),
            get_value(request['asset']['tiers'], 'tier1', 'name'),
            get_value(request['asset']['tiers'], 'tier1', 'external_id'),
            get_value(request['asset']['tiers'], 'tier2', 'id'),
            get_value(request['asset']['tiers'], 'tier2', 'name'),
            get_value(request['asset']['tiers'], 'tier2', 'external_id'),
            get_value(request['asset']['connection'], 'provider', 'id'),
            get_value(request['asset']['connection'], 'provider', 'name'),
            get_value(request['asset']['connection'], 'vendor', 'id'),
            get_value(request['asset']['connection'], 'vendor', 'name'),
            get_value(request['asset'], 'product', 'id'),
            get_value(request['asset'], 'product', 'name'),
            get_value(request, 'asset', 'id'),
            get_value(request, 'asset', 'external_id'),
            get_value(request['asset'], 'connection', 'type'),
            get_value(connection, 'hub', 'id') if 'hub' in connection else '',
            get_value(connection, 'hub', 'name') if 'hub' in connection else '',
            get_value(request, 'asset', 'status'),
            get_basic_value(request, 'reason'),
        )

        progress += 1
        progress_callback(progress, total)


def _get_requests(client, parameters):
    query = R()
    query &= R().created.ge(parameters['date']['after'])
    query &= R().created.le(parameters['date']['before'])

    if parameters.get('product') and parameters['product']['all'] is False:
        query &= R().asset.product.id.oneof(parameters['product']['choices'])
    if parameters.get('rr_type') and parameters['rr_type']['all'] is False:
        query &= R().type.oneof(parameters['rr_type']['choices'])
    query &= R().status.eq('failed')
    if parameters.get('connection_type') and parameters['connection_type']['all'] is False:
        query &= R().asset.connection.type.oneof(parameters['connection_type']['choices'])

    return client.requests.filter(query)
