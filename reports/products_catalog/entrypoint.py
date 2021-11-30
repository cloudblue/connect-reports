# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#

from datetime import date

from connect.client.rql import R


def generate(client, parameters, progress_callback, renderer_type, extra_context):

    account = client.collection('accounts').all().first()
    account_id = account['id']
    agreements_filter = R().type.eq('service')

    available_products = {}
    agreements_count = 0
    for agreement in client.agreements.filter(agreements_filter):
        if agreement['owner']['id'] != account_id:
            agreements_count += 1
            for product in client.collection(
                    'agreements',
            ).resource(
                agreement['id'],
            ).collection(
                'products',
            ).all():
                if not product['id'] in available_products:
                    available_products[product['id']] = product
                    available_products[product['id']]['agreements'] = [agreement['id']]
                else:
                    available_products[product['id']]['agreements'].append(agreement['id'])
    i = 0
    count = len(available_products) * 2
    ctx = {
        'products_count': len(available_products),
        'vendors_count': 0,
        'distributors_count': agreements_count,
        'generation_date': date.today().strftime('%B %d, %Y'),
        'api_url': client.endpoint.replace('/public/v1', ''),
        'account_name': account['name'],
        'account_id': account['id'],
    }

    vendors = set()

    data = []

    for prod in available_products:
        i += 1
        available_products[prod]['marketplaces'] = []
        for agreement in available_products[prod]['agreements']:
            marketplaces = client.collection(
                'agreements',
            ).resource(
                agreement,
            ).collection(
                'products',
            ).resource(
                prod,
            ).collection(
                'marketplaces',
            ).all()
            for marketplace in marketplaces:
                available_products[prod]['marketplaces'].append(marketplace)
        progress_callback(i, count)

    for prod in client.collection('products').all().order_by('name'):
        if prod['id'] in available_products:
            prod['marketplaces'] = available_products[prod['id']]['marketplaces']
            data.append(prod)
            vendors.add(prod['owner']['id'])
        i += 1
        progress_callback(i, count)

    ctx['vendors_count'] = len(vendors)
    extra_context(ctx)

    return data
