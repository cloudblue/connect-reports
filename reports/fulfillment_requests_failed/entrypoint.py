# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from cnct import R
from datetime import datetime
from reports.utils import convert_to_datetime, get_value, get_basic_value


def generate(client, parameters, progress_callback):

    all_types = ['tiers_setup', 'inquiring', 'pending', 'approved', 'failed', 'draft']
    query = R()
    query &= R().created.ge(parameters['date']['after'])
    query &= R().created.le(parameters['date']['before'])
    if parameters['product']:
        query &= R().asset.product.id.oneof(parameters['product'])
    if parameters['rr_type']:
        query &= R().type.oneof(parameters['rr_type'])
    else:
        query &= R().status.oneof(all_types)
    query &= R().status.eq('failed')
    if parameters['connection_type']:
        query &= R().asset.connection.type.oneof(parameters['connection_type'])
    requests = client.requests.filter(query)
    progress = 0
    total = requests.count()
    today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    for request in requests:
        connection = request['asset']['connection']
        yield (
            get_basic_value(request, 'id'),
            get_basic_value(request, 'type'),
            convert_to_datetime(
                get_basic_value(request, 'created')
            ),
            convert_to_datetime(
                get_basic_value(request, 'updated')
            ),
            today,
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
