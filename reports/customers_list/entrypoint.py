# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from cnct import R
from reports.utils import get_value, get_basic_value


def generate(client, parameters, progress_callback):
    query = R()
    if parameters.get('date') and parameters['date']['after'] != '':
        query &= R().created.ge(parameters['date']['after'])
        query &= R().created.le(parameters['date']['before'])
    if parameters.get('mkp') and parameters['mkp']['all'] is False:
        query &= R().asset.marketplace.id.oneof(parameters['mkp']['choices'])
    if parameters.get('tier_type') and parameters['tier_type']['all'] is False:
        query &= R().scopes.oneof(parameters['tier_type']['choices'])

    marketplaces_list = client.marketplaces.all()
    marketplaces = {}
    for marketplace in marketplaces_list:
        marketplaces[marketplace['id']] = {
            'name': marketplace['owner']['name'],
            'id': marketplace['owner']['id'],
        }
    customers = client.ns('tier').accounts.filter(query).order_by('-created').limit(1000)
    progress = 0
    total = customers.count()

    output = []

    def get_provider(mkp, prop):
        if not mkp or mkp == '-' or mkp not in marketplaces:  # pragma: no branch
            return '-'  # pragma: no cover
        return marketplaces[mkp][prop]

    def create_phone(pn):
        return f'{pn["country_code"]}{pn["area_code"]}{pn["phone_number"]}{pn["extension"]}'

    for customer in customers:
        try:
            customer_row = [
                get_basic_value(customer, 'id'),
                get_basic_value(customer, 'external_id'),
                get_basic_value(customer, 'environment'),
                'Yes' if 'customer' in customer['scopes'] else '-',
                'Yes' if 'tier1' in customer['scopes'] else '-',
                'Yes' if 'tier2' in customer['scopes'] else '-',
                get_provider(get_value(customer, 'marketplace', 'id'), 'id'),
                get_provider(get_value(customer, 'marketplace', 'id'), 'name'),
                get_value(customer, 'marketplace', 'id'),
                get_value(customer, 'marketplace', 'name'),
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
                    create_phone(contact['contact']['phone_number'])
                ]
            else:
                customer_row_extended = ['-'] * 10
            output.append(
                customer_row + customer_row_extended
            )

        except Exception:
            progress += 1
            progress_callback(progress, total)
            pass
        progress += 1
        progress_callback(progress, total)

    return output
