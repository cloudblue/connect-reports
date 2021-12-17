# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from connect.client import R

from ..utils import convert_to_datetime, get_basic_value, get_value, today_str

HEADERS = (
    'Request ID', 'Request Type',
    'Created At', 'Updated At', 'Exported At',
    'Request Status', 'Environment',
    'Tier Configuration ID', 'Tier Level',
    'Name', 'Tier External ID', 'Tier ID',
    'Parent Configuration ID', 'Parent Tier Level', 'Parent Name',
    'Parent External ID', 'Parent Tier ID',
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
    requests = _get_requests(client, parameters)
    total = requests.count()
    progress = 0
    if renderer_type == 'csv':
        yield HEADERS
        progress += 1
        total += 1
        progress_callback(progress, total)

    for request in requests:
        config = request['configuration']
        if renderer_type == 'json':
            yield {
                HEADERS[idx].replace(' ', '_').lower(): value
                for idx, value in enumerate(_process_line(request, config))
            }
        else:
            yield _process_line(request, config)
        progress += 1
        progress_callback(progress, total)


def _get_requests(client, parameters):
    all_types = ['tiers_setup', 'inquiring', 'pending', 'approved', 'failed']

    query = R()
    query &= R().events.created.at.ge(parameters['date']['after'])
    query &= R().events.created.at.le(parameters['date']['before'])

    if parameters.get('product') and parameters['product']['all'] is False:
        query &= R().product.id.oneof(parameters['product']['choices'])
    if parameters.get('mkp') and parameters['mkp']['all'] is False:
        query &= R().marketplace.id.oneof(parameters['mkp']['choices'])
    if parameters.get('rr_type') and parameters['rr_type']['all'] is False:
        query &= R().type.oneof(parameters['rr_type']['choices'])
    if parameters.get('rr_status') and parameters['rr_status']['all'] is False:
        query &= R().status.oneof(parameters['rr_status']['choices'])
    else:
        query &= R().status.oneof(all_types)

    return client.ns('tier').collection('config-requests').filter(query).order_by('-created')


def _process_line(request, config):
    return (
        get_basic_value(request, 'id'),
        get_basic_value(request, 'type'),
        convert_to_datetime(get_value(request['events'], 'created', 'at')),
        convert_to_datetime(get_value(request['events'], 'updated', 'at')),
        today_str(),
        get_basic_value(request, 'status'),
        get_value(
            config,
            'connection',
            'type',
        ),
        get_value(request, 'configuration', 'id'),
        get_value(request, 'configuration', 'tier_level'),
        get_value(config, 'account', 'name'),
        get_value(config, 'account', 'external_id'),
        get_value(config, 'account', 'id'),
        get_value(request, 'parent_configuration', 'id'),
        get_value(request, 'parent_configuration', 'tier_level'),
        get_value(
            request['parent_configuration'],
            'account',
            'name',
        ) if 'parent_configuration' in request else '-',
        get_value(
            request['parent_configuration'],
            'account',
            'external_id',
        ) if 'parent_configuration' in request else '-',
        get_value(
            request['parent_configuration'],
            'account',
            'id',
        ) if 'parent_configuration' in request else '-',
        get_value(
            config['connection'],
            'provider',
            'id',
        ) if 'connection' in config else '-',
        get_value(
            config['connection'],
            'provider',
            'name',
        ) if 'connection' in config else '-',
        get_value(
            config['connection'],
            'vendor',
            'id',
        ) if 'connection' in config else '-',
        get_value(
            config['connection'],
            'vendor',
            'name',
        ) if 'connection' in config else '-',
        get_value(
            config,
            'product',
            'id',
        ),
        get_value(
            config,
            'product',
            'name',
        ),
        get_value(
            config['connection'],
            'hub',
            'id',
        ) if 'connection' in config else '-',
        get_value(
            config['connection'],
            'hub',
            'name',
        ) if 'connection' in config else '-',
        get_value(
            config,
            'contract',
            'id',
        ),
        get_value(
            config,
            'marketplace',
            'id',
        ),
        get_value(
            config,
            'marketplace',
            'name',
        ),
    )
