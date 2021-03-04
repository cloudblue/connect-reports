# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from cnct import R

from datetime import datetime

from reports.utils import convert_to_datetime, get_basic_value, get_value


def generate(client, parameters, progress_callback):
    all_status = ['draft', 'reviewing', 'deploying', 'completed', 'canceled']
    query = R()
    if parameters.get('date') and parameters['date']['after'] != '':
        query &= R().created.ge(parameters['date']['after'])
        query &= R().created.le(parameters['date']['before'])
    if parameters.get('product') and parameters['product']['all'] is False:
        query &= R().listing.product.id.oneof(parameters['product']['choices'])
    if parameters.get('mkp') and parameters['mkp']['all'] is False:
        query &= R().listing.contract.marketplace.id.oneof(parameters['mkp']['choices'])
    if parameters.get('rr_status') and parameters['rr_status']['all'] is False:
        query &= R().state.oneof(parameters['rr_status']['choices'])
    else:
        query &= R().state.oneof(all_status)
    requests = client.listing_requests.filter(query).order_by("-created")
    progress = 0
    total = requests.count()
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    for request in requests:
        yield (
            get_basic_value(request, 'id'),
            get_basic_value(request, 'type'),
            get_basic_value(request, 'state'),
            convert_to_datetime(
                get_basic_value(request, 'created'),
            ),
            convert_to_datetime(
                get_basic_value(request, 'updated'),
            ),
            today,
            get_value(request, 'listing', 'id'),
            get_value(request['listing'], 'contract', 'id'),
            get_value(request, 'product', 'id'),
            get_value(request, 'product', 'name'),
            get_value(request['listing'], 'provider', 'id'),
            get_value(request['listing'], 'provider', 'name'),
            get_value(request['listing'], 'vendor', 'id'),
            get_value(request['listing'], 'vendor', 'name'),
        )
        progress += 1
        progress_callback(progress, total)
