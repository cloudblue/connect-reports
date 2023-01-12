# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue
# All rights reserved.
#

from connect.client import R

from ..utils import convert_to_datetime, get_basic_value, get_value

HEADERS = (
    'Case ID', 'Type', 'Status', 'Created At', 'Resolved At', 'Subject',
    'Priority', 'Issuer Account ID', 'Issuer Name', 'Issuer User Name',
    'Receiver Account ID', 'Receiver Name', 'Receiver User Name',
)


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    tickets = _get_tickets(client, parameters)
    progress = 0
    total = tickets.count()
    if renderer_type == 'csv':
        yield HEADERS
        progress += 1
        total += 1
        progress_callback(progress, total)

    for ticket in tickets:
        if renderer_type == 'json':
            yield {
                HEADERS[idx].replace(' ', '_').lower(): value
                for idx, value in enumerate(_process_line(ticket))
            }
        else:
            yield _process_line(ticket)
        progress += 1
        progress_callback(progress, total)


def _get_tickets(client, parameters):
    query = R()
    query &= R().events.created.at.ge(parameters['date']['after'])
    query &= R().events.created.at.le(parameters['date']['before'])

    if parameters.get('ticket_status') and parameters['ticket_status']['all'] is False:
        query &= R().state.oneof(parameters['ticket_status']['choices'])

    return client.ns('helpdesk').collection('cases').filter(query)


def _process_line(ticket):
    return (
        get_basic_value(ticket, 'id'),
        get_basic_value(ticket, 'type'),
        get_basic_value(ticket, 'state'),
        convert_to_datetime(
            get_value(ticket['events'], 'created', 'at'),
        ),
        convert_to_datetime(
            get_value(ticket['events'], 'resolved', 'at'),
        ) if 'resolved' in ticket['events'] else '-',
        get_basic_value(ticket, 'subject'),
        priority_to_string(get_basic_value(ticket, 'priority')),
        get_value(ticket['issuer'], 'account', 'id'),
        get_value(ticket['issuer'], 'account', 'name'),
        get_value(ticket['issuer'], 'agent', 'name'),
        get_value(ticket['receiver'], 'account', 'id'),
        get_value(ticket['receiver'], 'account', 'name'),
        get_value(ticket['receiver'], 'agent', 'name'),
    )


def priority_to_string(prio):
    prios = [
        'Low',
        'Medium',
        'High',
        'Urgent',
    ]
    priority = 'Low'
    try:
        priority = prios[prio]
    except IndexError:
        pass
    return priority
