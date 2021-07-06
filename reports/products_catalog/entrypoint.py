# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#

from datetime import date

from connect.client.rql import R


def generate(client, parameters, progress_callback, renderer_type, extra_context):

    filters = R().visibility.catalog.eq(True) & R().status.eq('published')

    count = client.products.filter(filters).count()

    i = 0

    ctx = {
        'products_count': count,
        'vendors_count': 0,
        'generation_date': date.today().strftime('%B %d, %Y'),
        'api_url': client.endpoint.replace('/public/v1', ''),
    }

    vendors = set()

    data = []

    for prod in client.products.filter(filters).order_by("name"):
        i += 1
        data.append(prod)
        vendors.add(prod['owner']['id'])
        progress_callback(i, count)

    ctx['vendors_count'] = len(vendors)
    extra_context(ctx)

    return data
