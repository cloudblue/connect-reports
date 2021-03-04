# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from cnct import R

from datetime import datetime

from reports.utils import convert_to_datetime, get_basic_value, get_value


def generate(client, parameters, progress_callback):
    all_status = ['listed', 'unlisted']
    query = R()
    if parameters.get('date') and parameters['date']['after'] != '':
        query &= R().created.ge(parameters['date']['after'])
        query &= R().created.le(parameters['date']['before'])
    if parameters.get('product') and parameters['product']['all'] is False:
        query &= R().product.id.oneof(parameters['product']['choices'])
    if parameters.get('mkp') and parameters['mkp']['all'] is False:
        query &= R().contract.marketplace.id.oneof(parameters['mkp']['choices'])
    if parameters.get('rr_status') and parameters['rr_status']['all'] is False:
        query &= R().state.oneof(parameters['rr_status']['choices'])
    else:
        query &= R().state.oneof(all_status)
    listings = client.listings.filter(query).order_by("-created")
    progress = 0
    total = listings.count()
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    for listing in listings:
        yield (
            get_basic_value(listing, 'id'),
            get_basic_value(listing, 'status'),
            convert_to_datetime(
                get_basic_value(listing, 'created'),
            ),
            convert_to_datetime(
                get_basic_value(listing, 'updated'),
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
