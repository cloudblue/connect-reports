# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from cnct import R
from datetime import datetime
from reports.utils import convert_to_datetime, get_value, get_basic_value


def generate(client, parameters, progress_callback):
    all_status = ['listed', 'unlisted']
    query = R()
    if parameters['date']:
        query &= R().created.ge(parameters['date']['after'])
        query &= R().created.le(parameters['date']['before'])
    if parameters['product']:
        query &= R().product.id.oneof(parameters['product'])
    if parameters['mkp']:
        query &= R().contract.marketplace.id.oneof(parameters['mkp'])
    if parameters['rr_status']:
        query &= R().state.oneof(parameters['rr_status'])
    else:
        query &= R().state.oneof(all_status)
    listings = client.listings.filter(query).order_by("-created")
    progress = 0
    total = listings.count()
    output = []
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    for listing in listings:
        yield (
            get_basic_value(listing, 'id'),
            get_basic_value(listing, 'status'),
            convert_to_datetime(
                get_basic_value(listing, 'created')
            ),
            convert_to_datetime(
                get_basic_value(listing, 'updated')
            ),
            today,
            get_value(listing, 'contract', 'id'),
            get_value(listing, 'product', 'id'),
            get_value(listing, 'product', 'name'),
            get_value(listing, 'provider', 'id'),
            get_value(listing, 'provider', 'name'),
            get_value(listing, 'vendor', 'id'),
            get_value(listing, 'vendor', 'name'),
        )
        progress += 1
        progress_callback(progress, total)

    return output
