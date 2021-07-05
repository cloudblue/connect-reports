# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from connect.client import R

from reports.utils import Progress, convert_to_datetime, get_basic_value, get_value

from concurrent import futures

from connect.client import ClientError

HEADERS = (
    'Asset ID', 'Asset External ID', 'Asset Status',
    'Asset Created At', 'Asset Updated At',
    'Customer ID', 'Customer Name', 'Customer External ID',
    'Tier 1 ID', 'Tier 1 Name', 'Tier 1 External ID',
    'Tier 2 ID', 'Tier 2 Name', 'Tier 2 External ID',
    'Provider ID', 'Provider Name',
    'Vendor ID', 'Vendor Name',
    'Product ID', 'Product Name',
    'Hub ID', 'Hub Name',
    'Usage Reports Count', 'Usage Reports IDs',
)


def get_record(
    client,
    asset,
    start_date,
    end_date,
    progress,
    renderer_type=None,
):
    rql = f"eq(asset.id,{asset['id']}),in(status,(approved,closed)),(and(ge(start_date,"
    rql += f"{start_date}),lt(start_date,{end_date}))|and(ge(end_date,{start_date}),"
    rql += f"lt(end_date,{end_date})))"
    usage_records = client.ns('usage').records.filter(rql)
    uf = []
    for record in usage_records:
        if record['usagefile']['id'] not in uf:
            uf.append(record['usagefile']['id'])
    progress.increment()
    if renderer_type == 'json':
        return {
            HEADERS[idx].replace(' ', '_').lower(): value
            for idx, value in enumerate(_process_line(asset, uf))
        }
    return _process_line(asset, uf)


def _process_line(asset, uf):
    return (
        get_basic_value(asset, 'id'),
        get_basic_value(asset, 'external_id'),
        get_basic_value(asset, 'status'),
        convert_to_datetime(asset['events']['created']['at']),
        convert_to_datetime(asset['events']['updated']['at']),
        get_value(asset['tiers'], 'customer', 'id'),
        get_value(asset['tiers'], 'customer', 'name'),
        get_value(asset['tiers'], 'customer', 'external_id'),
        get_value(asset['tiers'], 'tier1', 'id'),
        get_value(asset['tiers'], 'tier1', 'name'),
        get_value(asset['tiers'], 'tier1', 'external_id'),
        get_value(asset['tiers'], 'tier2', 'id'),
        get_value(asset['tiers'], 'tier2', 'name'),
        get_value(asset['tiers'], 'tier2', 'external_id'),
        get_value(asset['connection'], 'provider', 'id'),
        get_value(asset['connection'], 'provider', 'name'),
        get_value(asset['connection'], 'vendor', 'id'),
        get_value(asset['connection'], 'vendor', 'name'),
        get_value(asset, 'product', 'id'),
        get_value(asset, 'product', 'name'),
        get_value(asset['connection'], 'hub', 'id'),
        get_value(asset['connection'], 'hub', 'name'),
        len(uf),
        ', '.join(uf),
    )


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    product_rql = R().status.eq('active')

    if parameters.get('product') and parameters['product']['all'] is False:
        product_rql &= R().product.id.oneof(parameters['product']['choices'])

    assets = client.ns('subscriptions').assets.filter(product_rql)

    total = assets.count()
    start_date = parameters['period']['after']
    end_date = parameters['period']['before']

    ex = futures.ThreadPoolExecutor()
    if renderer_type == 'csv':
        total += 1
        progress = Progress(progress_callback, total)
        progress.increment()
        yield HEADERS
    else:
        progress = Progress(progress_callback, total)

    wait_for = []
    try:
        for asset in assets:
            wait_for.append(
                ex.submit(
                    get_record,
                    client,
                    asset,
                    start_date,
                    end_date,
                    progress,
                    renderer_type,
                ),
            )
        for future in futures.as_completed(wait_for):
            yield future.result()
    except ClientError:  # pragma: no cover
        for future in wait_for:
            future.cancel()
        raise
