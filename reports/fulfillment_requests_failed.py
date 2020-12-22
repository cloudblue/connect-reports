# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from cnct import R
from datetime import datetime


def generate(client, parameters, progress_callback):
    query = R()
    query &= R().created.ge(parameters['date']['after'])
    query &= R().created.le(parameters['date']['before'])
    if parameters['product']:
        query &= R().asset.product.id.oneof(parameters['product'])
    if parameters['rr_type']:
        query &= R().type.oneof(parameters['rr_type'])
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
            request['id'],
            request['type'],
            today,
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
            request['status'],
            request['reason'],
        )

        progress += 1
        progress_callback(progress, total)
