# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue
# All rights reserved.
#

from connect.client import R

from ..utils import convert_to_datetime, get_basic_value, get_value, today_str

HEADERS = (
    'Request ID', 'Request Type', 'Request Status',
    'Created At', 'Updated At', 'Exported At',
    'Customer ID', 'Customer Name', 'Customer External ID',
    'Tier 1 ID', 'Tier 1 Name', 'Tier 1 External ID',
    'Tier 2 ID', 'Tier 2 Name', 'Tier 2 External ID',
    'Marketplace ID', 'Marketplace Name',
    'Provider  ID', 'Provider Name', 'Vendor ID', 'Vendor Name',
    'Product ID', 'Product Name',
    'Asset ID', 'Asset External ID', 'Transaction Type',
    'Hub ID', 'Hub Name', 'Asset Status',
)


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    requests = _get_requests(client, parameters)
    progress = 0
    total = requests.count()
    if renderer_type == 'csv':
        yield HEADERS
        progress += 1
        total += 1
        progress_callback(progress, total)

    for request in requests:
        connection = request['asset']['connection']
        if renderer_type == 'json':
            yield {
                HEADERS[idx].replace(' ', '_').lower(): value
                for idx, value in enumerate(_process_line(request, connection))
            }
        else:
            yield _process_line(request, connection)
        progress += 1
        progress_callback(progress, total)


def _get_requests(client, parameters):
    all_status = ['tiers_setup', 'inquiring', 'pending', 'approved', 'failed']

    query = R()
    query &= R().created.ge(parameters['date']['after'])
    query &= R().created.le(parameters['date']['before'])

    if parameters.get('product') and parameters['product']['all'] is False:
        query &= R().asset.product.id.oneof(parameters['product']['choices'])
    if parameters.get('rr_type') and parameters['rr_type']['all'] is False:
        query &= R().type.oneof(parameters['rr_type']['choices'])
    if parameters.get('rr_status') and parameters['rr_status']['all'] is False:
        query &= R().status.oneof(parameters['rr_status']['choices'])
    else:
        query &= R().status.oneof(all_status)
    if parameters.get('mkp') and parameters['mkp']['all'] is False:
        query &= R().asset.marketplace.id.oneof(parameters['mkp']['choices'])
    if parameters.get('hub') and parameters['hub']['all'] is False:
        query &= R().asset.connection.hub.id.oneof(parameters['hub']['choices'])

    return client.requests.filter(query).select(
        '-asset.items',
        '-asset.params',
        '-asset.configuration',
        '-activation_key',
        '-template',
    )


def _process_line(request, connection):
    return (
        get_basic_value(request, 'id'),
        get_basic_value(request, 'type'),
        get_basic_value(request, 'status'),
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
        get_value(request['asset'], 'marketplace', 'id'),
        get_value(request['asset'], 'marketplace', 'name'),
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
    )
