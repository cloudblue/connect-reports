from cnct import R

from reports.utils import convert_to_datetime, get_value


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


def generate(client, parameters, progress_callback):
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

    subscriptions = client.ns('subscriptions').assets.filter(query)
    progress = 0
    total = subscriptions.count()

    for subscription in subscriptions:
        yield (
            subscription.get('id'),
            subscription.get('external_id', '-'),
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
        progress += 1
        progress_callback(progress, total)
