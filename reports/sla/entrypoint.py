# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#
import datetime

from connect.client import R

from ..utils import convert_to_datetime, get_dict_element


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    try:
        offset_red = int(parameters['offset_red_days'])
        offset_yellow = int(parameters['offset_yellow_days'])

    except Exception:
        raise RuntimeError("Yellow and Red zone must be defined as amount of days")

    if offset_red <= offset_yellow:
        raise RuntimeError("Red zone must be for more days than yellow one")

    query = R()
    query &= R().status.eq('pending')
    if parameters.get('trans_type') and parameters['trans_type']['all'] is False:
        query &= R().asset.connection.type.oneof(parameters['trans_type']['choices'])
    if parameters.get('product') and parameters['product']['all'] is False:
        query &= R().asset.product.id.oneof(parameters['product']['choices'])
    requests = client.requests.filter(query).select(
        '-asset.items',
        '-asset.params',
        '-asset.configuration',
    ).order_by('created')

    total = requests.count()

    progress = 0

    levels = {
        'red': offset_red,
        'yellow': offset_yellow,
    }

    for request in requests:
        yield _process_line(request, levels)
        progress += 1
        progress_callback(progress, total)


def _get_awaiting_for(data):
    return (datetime.datetime.utcnow() - convert_to_datetime(data['created'])).days


def _get_contact(data):
    if not data:
        return ''
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
        _get_contact(data['asset']['tiers'].get('customer')),
        get_dict_element(data, 'asset', 'tiers', 'customer', 'contact_info', 'contact', 'email'),
        get_dict_element(data, 'asset', 'tiers', 'tier1', 'name'),
        get_dict_element(data, 'asset', 'tiers', 'tier1', 'external_id'),
        _get_contact(data['asset']['tiers'].get('tier1')),
        get_dict_element(data, 'asset', 'tiers', 'tier1', 'contact_info', 'contact', 'email'),
        get_dict_element(data, 'asset', 'tiers', 'tier2', 'name'),
        get_dict_element(data, 'asset', 'tiers', 'tier2', 'external_id'),
        _get_contact(data['asset']['tiers'].get('tier2')),
        get_dict_element(data, 'asset', 'tiers', 'tier2', 'contact_info', 'contact', 'email'),
        get_dict_element(data, 'marketplace', 'id'),
        get_dict_element(data, 'marketplace', 'name'),
        sla_level,
    )
