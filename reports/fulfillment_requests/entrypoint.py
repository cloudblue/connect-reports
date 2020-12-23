# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from cnct import R
from datetime import datetime


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

    query = R()
    query &= R().created.ge(parameters['date']['after'])
    query &= R().created.le(parameters['date']['before'])
    if parameters['product']:
        query &= R().asset.product.id.oneof(parameters['product'])
    if parameters['rr_type']:
        query &= R().type.oneof(parameters['rr_type'])
    if parameters['rr_status']:
        query &= R().status.oneof(parameters['rr_status'])
    if parameters['mkp']:
        query &= R().asset.marketplace.id.oneof(parameters['mkp'])
    if parameters['hub']:
        query &= R().asset.connection.hub.id.oneof(parameters['hub'])

    requests = client.requests.filter(query)
    progress = 0
    total = requests.count()

    today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    for request in requests:
        connection = request['asset']['connection']
        for item in request['asset']['items']:
            yield (
                request['id'],
                request['type'],
                today,
                item['global_id'],
                item['display_name'],
                item['item_type'],
                item['type'],
                item['mpn'],
                item['period'],
                item['quantity'],
                request['asset']['tiers']['customer']['id'],
                request['asset']['tiers']['customer']['name'],
                request['asset']['tiers']['customer'].get('external_id', ''),
                request['asset']['connection']['provider']['id'],
                request['asset']['connection']['provider']['name'],
                request['asset']['connection']['vendor']['id'],
                request['asset']['connection']['vendor']['name'],
                request['asset']['product']['id'],
                request['asset']['product']['name'],
                request['asset']['id'],
                request['asset'].get('external_id', ''),
                request['asset']['connection']['type'],
                connection['hub']['id'] if 'hub' in connection else '',
                connection['hub']['name'] if 'hub' in connection else '',
                request['status']
            )
        progress += 1
        progress_callback(progress, total)
