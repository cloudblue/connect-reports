from cnct import R

from reports.utils import convert_to_datetime, get_basic_value, get_value

from datetime import datetime


def generate(client, parameters, progress_callback):
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

    configurations = client.ns('tier').configs.filter(query).order_by('-created')
    progress = 0
    total = configurations.count()
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    for configuration in configurations:
        yield(
            get_basic_value(configuration, 'id'),
            get_basic_value(configuration, 'tier_level'),
            convert_to_datetime(get_value(configuration['events'], 'created', 'at')),
            convert_to_datetime(get_value(configuration['events'], 'updated', 'at')),
            today,
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

        progress += 1
        progress_callback(progress, total)
