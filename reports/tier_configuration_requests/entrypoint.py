from cnct import R

from reports.utils import convert_to_datetime, get_basic_value, get_value

from datetime import datetime


def generate(client, parameters, progress_callback):
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

    requests = client.ns('tier').collection('config-requests').filter(query).order_by('-created')
    progress = 0
    total = requests.count()
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    for request in requests:
        config = request['configuration']
        yield(
            get_basic_value(request, 'id'),
            get_basic_value(request, 'type'),
            convert_to_datetime(get_value(request['events'], 'created', 'at')),
            convert_to_datetime(get_value(request['events'], 'updated', 'at')),
            today,
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

        progress += 1
        progress_callback(progress, total)
