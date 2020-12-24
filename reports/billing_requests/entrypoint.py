# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from cnct import R
from reports.utils import convert_to_datetime, get_value, get_basic_value


def generate(client, parameters, progress_callback):
    query = R()
    query &= R().created.ge(parameters['date']['after'])
    query &= R().created.le(parameters['date']['before'])
    if parameters['product']:
        query &= R().asset.product.id.oneof(parameters['product'])
    if parameters['mkp']:
        query &= R().asset.marketplace.id.oneof(parameters['mkp'])
    if parameters['hub']:
        query &= R().asset.connection.hub.id.oneof(parameters['hub'])

    requests = client.ns('subscriptions').requests.filter(query)
    progress = 0
    total = requests.count()
    output = []
    for request in requests:
        connection = request['asset']['connection']
        for item in request['items']:
            output.append([
                request['id'],
                convert_to_datetime(request['period']['from']),
                convert_to_datetime(request['period']['to']),
                get_basic_value(request['period'], 'delta'),
                get_basic_value(request['period'], 'uom'),
                get_basic_value(item['billing'], 'cycle_number'),
                get_basic_value(item, 'global_id'),
                get_basic_value(item, 'display_name'),
                get_basic_value(item, 'item_type'),
                get_basic_value(item, 'type'),
                get_basic_value(item, 'mpn'),
                get_basic_value(item, 'period'),
                get_basic_value(item, 'quantity'),
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
                get_value(request, 'asset', 'status'),
                get_value(request['asset'], 'connection', 'type'),
                get_value(connection, 'hub', 'id') if 'hub' in connection else '',
                get_value(connection, 'hub', 'name') if 'hub' in connection else '',
            ])
        progress += 1
        progress_callback(progress, total)

    return output
