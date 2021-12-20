# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#

from connect.client import R

from ..utils import convert_to_datetime, get_value

HEADERS = (
    'Subscription ID', 'Subscription External ID', 'Subscription Type',
    'Creation date', 'Updated date', 'Status', 'Billing Period',
    'Anniversary Day', 'Anniversary Month', 'Contract ID', 'Contract Name',
    'Customer ID', 'Customer Name', 'Customer External ID',
    'Tier 1 ID', 'Tier 1 Name', 'Tier 1 External ID',
    'Tier 2 ID', 'Tier 2 Name', 'Tier 2 External ID',
    'Provider Account ID', 'Provider Account name',
    'Vendor Account ID', 'Vendor Account Name',
    'Product ID', 'Product Name', 'Hub ID', 'Hub Name',
)


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    subscriptions = _get_subscriptions(client, parameters)
    total = subscriptions.count()
    progress = 0
    if renderer_type == 'csv':
        yield HEADERS
        progress += 1
        total += 1
        progress_callback(progress, total)

    for subscription in subscriptions:
        if renderer_type == 'json':
            yield {
                HEADERS[idx].replace(' ', '_').lower(): value
                for idx, value in enumerate(_process_line(subscription))
            }
        else:
            yield _process_line(subscription)
        progress += 1
        progress_callback(progress, total)


def _get_subscriptions(client, parameters):
    query = R()
    if parameters.get('date') and parameters['date']['after'] != '':
        query &= R().events.created.at.ge(parameters['date']['after'])
        query &= R().events.created.at.le(parameters['date']['before'])
    if parameters.get('product') and parameters['product']['all'] is False:
        query &= R().product.id.oneof(parameters['product']['choices'])
    if parameters.get('mkp') and parameters['mkp']['all'] is False:
        query &= R().marketplace.id.oneof(parameters['mkp']['choices'])
    if parameters.get('period') and parameters['period']['all'] is False:
        query &= R().billing.period.uom.oneof(parameters['period']['choices'])
    if parameters.get('status') and parameters['status']['all'] is False:
        query &= R().status.oneof(parameters['status']['choices'])

    return client.ns('subscriptions').assets.filter(query)


def calculate_period(delta, uom):
    if delta == 1:
        if uom == 'monthly':
            return 'Monthly'
        return 'Yearly'
    else:
        if uom == 'monthly':
            return f'{int(delta)} Months'
        return f'{int(delta)} Years'


def get_anniversary_day(subscription_billing):
    if 'anniversary' in subscription_billing and 'day' in subscription_billing['anniversary']:
        return subscription_billing['anniversary']['day']
    return '-'


def get_anniversary_month(subscription_billing):
    if 'anniversary' in subscription_billing and 'month' in subscription_billing['anniversary']:
        return subscription_billing['anniversary']['month']
    return '-'


def _process_line(subscription):
    return (
        subscription.get('id'),
        subscription.get('external_id', '-'),
        get_value(subscription, 'connection', 'type'),
        convert_to_datetime(subscription['events']['created']['at']),
        convert_to_datetime(subscription['events']['updated']['at']),
        subscription.get('status'),
        calculate_period(
            subscription['billing']['period']['delta'],
            subscription['billing']['period']['uom'],
        ) if 'billing' in subscription else '-',
        get_anniversary_day(subscription['billing']) if 'billing' in subscription else '-',
        get_anniversary_month(subscription['billing']) if 'billing' in subscription else '-',
        subscription['contract']['id'] if 'contract' in subscription else '-',
        subscription['contract']['name'] if 'contract' in subscription else '-',
        get_value(subscription.get('tiers', ''), 'customer', 'id'),
        get_value(subscription.get('tiers', ''), 'customer', 'name'),
        get_value(subscription.get('tiers', ''), 'customer', 'external_id'),
        get_value(subscription.get('tiers', ''), 'tier1', 'id'),
        get_value(subscription.get('tiers', ''), 'tier1', 'name'),
        get_value(subscription.get('tiers', ''), 'tier1', 'external_id'),
        get_value(subscription.get('tiers', ''), 'tier2', 'id'),
        get_value(subscription.get('tiers', ''), 'tier2', 'name'),
        get_value(subscription.get('tiers', ''), 'tier2', 'external_id'),
        get_value(subscription['connection'], 'provider', 'id'),
        get_value(subscription['connection'], 'provider', 'name'),
        get_value(subscription['connection'], 'vendor', 'id'),
        get_value(subscription['connection'], 'vendor', 'name'),
        get_value(subscription, 'product', 'id'),
        get_value(subscription, 'product', 'name'),
        get_value(subscription['connection'], 'hub', 'id'),
        get_value(subscription['connection'], 'hub', 'name'),
    )
