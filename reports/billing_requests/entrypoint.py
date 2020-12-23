# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from cnct import R


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

    for request in requests:
        connection = request['asset']['connection']
        for item in request['items']:
            yield (
                request['id'],
                request['period']['from'].replace("T", " ").replace("+00:00", ""),
                request['period']['to'].replace("T", " ").replace("+00:00", ""),
                request['period']['delta'],
                request['period']['uom'],
                item['billing']['cycle_number'],
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
                request['asset']['status'],
                request['asset']['connection']['type'],
                connection['hub']['id'] if 'hub' in connection else '',
                connection['hub']['name'] if 'hub' in connection else '',
            )
        progress += 1
        progress_callback(progress, total)
