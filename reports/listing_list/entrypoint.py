# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from connect.client import R

from reports.utils import convert_to_datetime, get_basic_value, get_value, today_str

HEADERS = (
    'Listing ID', 'Status',
    'Created At', 'Updated At', 'Exported At',
    'Contract ID', 'Product ID', 'Product Name',
    'Provider ID', 'Provider Name',
    'Vendor ID', 'Vendor Name',
)


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    listings = _get_listings(client, parameters)
    total = listings.count()
    progress = 0
    if renderer_type == 'csv':
        yield HEADERS
        progress += 1
        total += 1
        progress_callback(progress, total)

    for listing in listings:
        if renderer_type == 'json':
            yield {
                HEADERS[idx].replace(' ', '_').lower(): value
                for idx, value in enumerate(_process_line(listing))
            }
        else:
            yield _process_line(listing)
        progress += 1
        progress_callback(progress, total)


def _get_listings(client, parameters):
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

    return client.listings.filter(query).order_by("-created")


def _process_line(listing):
    return (
        get_basic_value(listing, 'id'),
        get_basic_value(listing, 'status'),
        convert_to_datetime(
            get_basic_value(listing, 'created'),
        ),
        convert_to_datetime(
            get_basic_value(listing, 'updated'),
        ),
        today_str(),
        get_value(listing, 'contract', 'id'),
        get_value(listing, 'product', 'id'),
        get_value(listing, 'product', 'name'),
        get_value(listing, 'provider', 'id'),
        get_value(listing, 'provider', 'name'),
        get_value(listing, 'vendor', 'id'),
        get_value(listing, 'vendor', 'name'),
    )
