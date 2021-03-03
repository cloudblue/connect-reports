# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from cnct import R
from reports.utils import get_value, get_basic_value, Progress
from concurrent import futures


def generate(client, parameters, progress_callback):
    query = R()
    if parameters.get('date') and parameters['date']['after'] != '':
        query &= R().created.ge(parameters['date']['after'])
        query &= R().created.le(parameters['date']['before'])
    if parameters.get('tier_type') and parameters['tier_type']['all'] is False:
        query &= R().scopes.oneof(parameters['tier_type']['choices'])

    marketplaces_list = client.marketplaces.all()
    hubs = {}
    for marketplace in marketplaces_list:
        if 'hubs' in marketplace:
            for hub in marketplace['hubs']:
                if 'hub' in hub and hub['hub']['id'] not in hubs:
                    hubs[hub['hub']['id']] = marketplace['owner']

    customers = client.ns('tier').accounts.filter(query).order_by('-events.created.at').limit(1000)

    total = customers.count()
    progress = Progress(progress_callback, total)

    def get_provider(hub, prop):
        if not hub or hub == '-' or hub not in hubs:  # pragma: no branch
            return '-'  # pragma: no cover
        return hubs[hub][prop]

    def create_phone(pn):
        return f'{pn["country_code"]}{pn["area_code"]}{pn["phone_number"]}{pn["extension"]}'

    def get_record(client, customer, parameters, progress):

        customer_row = [
            get_basic_value(customer, 'id'),
            get_basic_value(customer, 'external_id'),
            'Yes' if 'customer' in customer['scopes'] else '-',
            'Yes' if 'tier1' in customer['scopes'] else '-',
            'Yes' if 'tier2' in customer['scopes'] else '-',
            get_provider(get_value(customer, 'hub', 'id'), 'id'),
            get_provider(get_value(customer, 'hub', 'id'), 'name'),
            get_basic_value(customer, 'name'),
            get_basic_value(customer, 'tax_id'),
        ]

        if parameters['full_contact_info'] == 'yes':
            customer_extended_info = client.ns('tier').accounts[
                get_basic_value(customer, 'id')
            ].get()

            contact = customer_extended_info['contact_info']
            customer_row_extended = [
                get_basic_value(contact, 'address_line1'),
                get_basic_value(contact, 'address_line2'),
                get_basic_value(contact, 'city'),
                get_basic_value(contact, 'state'),
                get_basic_value(contact, 'postal_code'),
                get_basic_value(contact, 'country'),
                get_value(contact, 'contact', 'first_name'),
                get_value(contact, 'contact', 'last_name'),
                get_value(contact, 'contact', 'email'),
                create_phone(contact['contact']['phone_number']),
                'Available',
            ]
        else:
            customer_row_extended = ['-'] * 10
            customer_row_extended.append('Not available')

        progress.increment()

        return customer_row + customer_row_extended

    ex = futures.ThreadPoolExecutor()

    wait_for = []

    for customer in customers:

        wait_for.append(
            ex.submit(
                get_record,
                client,
                customer,
                parameters,
                progress,
            )
        )

    for future in futures.as_completed(wait_for):
        yield future.result()
