# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from connect.client import R

from ..utils import convert_to_datetime, get_basic_value, get_value, today_str

HEADERS = (
    'Tier Configuration ID', 'Tier Level',
    'Created At', 'Updated At', 'Exported At',
    'Status', 'Environment', 'Name',
    'Tier External ID', 'Tier ID',
    'Provider ID', 'Provider Name',
    'Vendor ID', 'Vendor Name',
    'Product ID', 'Product Name',
    'Hub ID', 'Hub Name', 'Contract ID',
    'MarketPlace ID', 'Marketplace',
)


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    configurations = _get_configurations(client, parameters)
    total = configurations.count()
    progress = 0
    if renderer_type == 'csv':
        yield HEADERS
        progress += 1
        total += 1
        progress_callback(progress, total)

    for configuration in configurations:
        if renderer_type == 'json':
            yield {
                HEADERS[idx].replace(' ', '_').lower(): value
                for idx, value in enumerate(_process_line(configuration))
            }
        else:
            yield _process_line(configuration)

        progress += 1
        progress_callback(progress, total)


def _get_configurations(client, parameters):
    all_types = ['active', 'processing']
    query = R()

    if parameters.get("date") and parameters['date']['after'] != '':
        query &= R().events.created.at.ge(parameters['date']['after'])
        query &= R().events.created.at.le(parameters['date']['before'])
    if parameters.get('product') and parameters['product']['all'] is False:
        query &= R().product.id.oneof(parameters['product']['choices'])
    if parameters.get('mkp') and parameters['mkp']['all'] is False:
        query &= R().marketplace.id.oneof(parameters['mkp']['choices'])
    if parameters.get('rr_status') and parameters['rr_status']['all'] is False:
        query &= R().status.oneof(parameters['rr_status']['choices'])
    else:
        query &= R().status.oneof(all_types)

    return client.ns('tier').configs.filter(query).order_by('-created')


def _process_line(configuration):
    return (
        get_basic_value(configuration, 'id'),
        get_basic_value(configuration, 'tier_level'),
        convert_to_datetime(get_value(configuration['events'], 'created', 'at')),
        convert_to_datetime(get_value(configuration['events'], 'updated', 'at')),
        today_str(),
        get_basic_value(configuration, 'status'),
        get_value(
            configuration,
            'connection',
            'type',
        ),
        get_value(configuration, 'account', 'name'),
        get_value(configuration, 'account', 'external_id'),
        get_value(configuration, 'account', 'id'),
        get_value(
            configuration['connection'],
            'provider',
            'id',
        ) if 'connection' in configuration else '-',
        get_value(
            configuration['connection'],
            'provider',
            'name',
        ) if 'connection' in configuration else '-',
        get_value(
            configuration['connection'],
            'vendor',
            'id',
        ) if 'connection' in configuration else '-',
        get_value(
            configuration['connection'],
            'vendor',
            'name',
        ) if 'connection' in configuration else '-',
        get_value(
            configuration,
            'product',
            'id',
        ),
        get_value(
            configuration,
            'product',
            'name',
        ),
        get_value(
            configuration['connection'],
            'hub',
            'id',
        ) if 'connection' in configuration else '-',
        get_value(
            configuration['connection'],
            'hub',
            'name',
        ) if 'connection' in configuration else '-',
        get_value(
            configuration,
            'contract',
            'id',
        ),
        get_value(
            configuration,
            'marketplace',
            'id',
        ),
        get_value(
            configuration,
            'marketplace',
            'name',
        ),
    )
