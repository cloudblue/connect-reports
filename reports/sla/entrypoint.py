# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#
import datetime

from reports.utils import convert_to_datetime, get_dict_element


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    """
    Extracts data from Connect using the ConnectClient instance
    and input data provided as arguments, applies
    required transformations (if any) and returns the data rendered
    by the given renderer on the arguments list.
    Some renderers may require extra context data to generate the report
    output, for example in the case of the Jinja2 renderer...

    :param client: An instance of the CloudBlue Connect
                    client.
    :type client: cnct.ConnectClient
    :param input_data: Input data used to calculate the
                        resulting dataset.
    :type input_data: dict
    :param progress_callback: A function that accepts t
                                argument of type int that must
                                be invoked to notify the progress
                                of the report generation.
    :type progress_callback: func
    :param renderer_type: Renderer required for generating report
                            output.
    :type renderer_type: string
    :param extra_context_callback: Extra content required by some
                            renderers.
    :type extra_context_callback: func
    """
    offset_red = int(parameters['offset_red_days'])
    offset_yellow = int(parameters['offset_yellow_days'])

    generator = client.requests.all().order_by('created').limit(1000)

    total = client.requests.all().count()

    progress = 0

    levels = {
        'red': offset_red,
        'yellow': offset_yellow,
    }

    for record in generator:
        yield _process_line(record, levels)
        progress += 1
        progress_callback(progress, total)


def _get_awaiting_for(data):
    return (datetime.datetime.utcnow() - convert_to_datetime(data['created'])).days


def _get_contact(data):
    last_name = get_dict_element(data, 'contact_info', 'contact', 'last_name')
    first_name = get_dict_element(data, 'contact_info', 'contact', 'first_name')
    return f'{last_name} {first_name}' if last_name and first_name else ''


def _get_sla_level(awaiting_days, levels):
    if awaiting_days >= levels['red']:
        return 'RED'
    elif awaiting_days >= levels['yellow']:
        return 'YELLOW'
    else:
        return 'GREEN'


def _process_line(data, levels):
    awaiting_for_days = _get_awaiting_for(data)
    sla_level = _get_sla_level(awaiting_for_days, levels)
    return (
        data.get('id'),
        get_dict_element(data, 'asset', 'product', 'id'),
        get_dict_element(data, 'asset', 'product', 'name'),
        get_dict_element(data, 'asset', 'connection', 'vendor', 'id'),
        get_dict_element(data, 'asset', 'connection', 'vendor', 'name'),
        get_dict_element(data, 'asset', 'connection', 'provider', 'id'),
        get_dict_element(data, 'asset', 'connection', 'provider', 'name'),
        get_dict_element(data, 'type'),
        awaiting_for_days,
        convert_to_datetime(get_dict_element(data, 'created')),
        get_dict_element(data, 'status'),
        get_dict_element(data, 'asset', 'connection', 'type'),
        get_dict_element(data, 'assignee', 'email'),
        get_dict_element(data, 'asset', 'tiers', 'customer', 'id'),
        get_dict_element(data, 'asset', 'tiers', 'customer', 'external_id'),
        get_dict_element(data, 'asset', 'tiers', 'customer', 'name'),
        _get_contact(get_dict_element(data, 'asset', 'tiers', 'customer')),
        get_dict_element(data, 'asset', 'tiers', 'customer', 'contact_info', 'contact', 'email'),
        get_dict_element(data, 'asset', 'tiers', 'tier1', 'name'),
        get_dict_element(data, 'asset', 'tiers', 'tier1', 'external_id'),
        _get_contact(get_dict_element(data, 'asset', 'tiers', 'tier1')),
        get_dict_element(data, 'asset', 'tiers', 'tier1', 'contact_info', 'contact', 'email'),
        get_dict_element(data, 'asset', 'tiers', 'tier2', 'name'),
        get_dict_element(data, 'asset', 'tiers', 'tier2', 'external_id'),
        _get_contact(get_dict_element(data, 'asset', 'tiers', 'tier2')),
        get_dict_element(data, 'asset', 'tiers', 'tier2', 'contact_info', 'contact', 'email'),
        get_dict_element(data, 'marketplace', 'id'),
        get_dict_element(data, 'marketplace', 'name'),
        sla_level,
    )
