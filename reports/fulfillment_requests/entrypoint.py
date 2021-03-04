# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from cnct import R

from datetime import datetime

from reports.utils import convert_to_datetime, get_basic_value, get_value


def generate(client, parameters, progress_callback):
    """
    Extracts data from Connect using the ConnectClient instance
    and input parameters provided as arguments, applies
    required transformations (if any) and returns an iterator of rows
    that will be used to fill the Excel file.
    Each element returned by the iterator must be an iterator over
    the columns value.

    :param client: An instance of the CloudBlue Connect
                    client.
    :type client: cnct.ConnectClient
    :param parameters: Input parameters used to calculate the
                        resulting dataset.
    :type parameters: dict
    :param progress_callback: A function that accepts t
                                argument of type int that must
                                be invoked to notify the progress
                                of the report generation.
    :type progress_callback: func
    """
    all_types = ['tiers_setup', 'inquiring', 'pending', 'approved', 'failed', 'draft']
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
        query &= R().status.oneof(all_types)
    if parameters.get('mkp') and parameters['mkp']['all'] is False:
        query &= R().asset.marketplace.id.oneof(parameters['mkp']['choices'])
    if parameters.get('hub') and parameters['hub']['all'] is False:
        query &= R().asset.connection.hub.id.oneof(parameters['hub']['choices'])

    requests = client.requests.filter(query)
    progress = 0
    total = requests.count()

    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    for request in requests:
        connection = request['asset']['connection']
        for item in request['asset']['items']:
            yield (
                get_basic_value(request, 'id'),
                get_basic_value(request, 'type'),
                convert_to_datetime(
                    get_basic_value(request, 'created'),
                ),
                convert_to_datetime(
                    get_basic_value(request, 'updated'),
                ),
                today,
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
                get_value(request['asset'], 'connection', 'type'),
                get_value(connection, 'hub', 'id') if 'hub' in connection else '',
                get_value(connection, 'hub', 'name') if 'hub' in connection else '',
                get_value(request, 'asset', 'status'),
            )
        progress += 1
        progress_callback(progress, total)
