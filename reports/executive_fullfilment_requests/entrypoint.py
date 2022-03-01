# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#
import pathlib
from datetime import date
from tempfile import NamedTemporaryFile
from collections import namedtuple
import math
import copy

from connect.client import R
from plotly import graph_objects as go

from ..utils import (
    convert_to_datetime,
    get_dict_element,
    get_value,
)
from .constants import (
    COUNTRIES,
    ELEMENTS_PER_CHART,
    THRESHOLD,
)


Part = namedtuple('Part', ('start_index', 'end_index', 'part', 'total'))


def _get_requests(client, parameters):
    final_status = ('approved', 'failed', 'revoked')

    query = R()
    query &= R().created.ge(parameters['date']['after'])
    query &= R().created.le(parameters['date']['before'])
    query &= R().status.oneof(final_status)

    if parameters.get('product') and parameters['product']['all'] is False:
        query &= R().asset.product.id.oneof(parameters['product']['choices'])
    if parameters.get('rr_type') and parameters['rr_type']['all'] is False:
        query &= R().type.oneof(parameters['rr_type']['choices'])
    return client.requests.filter(query).select('-asset.params', '-asset.configuration')


def _get_request_count_group_by_type(client, parameters):
    final_status = (
        'approved', 'failed', 'revoked',
    )
    rr_types = ('adjustment', 'purchase', 'change', 'suspend', 'resume', 'cancel')
    filters = R().created.ge(parameters['date']['after'])
    filters &= R().created.le(parameters['date']['before'])
    filters &= R().status.oneof(final_status)

    if parameters.get('product') and parameters['product']['all'] is False:
        filters &= R().asset.product.id.oneof(parameters['product']['choices'])
    if parameters.get('rr_type') and parameters['rr_type']['all'] is False:
        rr_types = parameters['rr_type']['choices']

    result = {}
    for rtype in rr_types:
        result[rtype] = client.requests.filter(filters & R().type.eq(rtype)).count()

    return result, client.requests.filter(filters).count()


def _calculate_the_average_and_sort(report_data):
    for key, value in report_data.items():
        report_data[key]['avg'] = round(
            sum(value['provision_times']) / len(value['provision_times']),
            2,
        )
    return dict(sorted(report_data.items(), key=lambda d: d[1]['avg'], reverse=True))


def _generate_pie_chart(
    labels,
    values,
    title=None,
    portions_colors=None,
    show_legend=False,
    show_values=False,
):
    """
    Function that creates a PIE graph using the plotly library. The styling has been preconfigured
     but could be changed.

    The styling could be customized, this means moving elements position, the font and their
     colors, personalize background colors, etc. Take a look at the official documentation.

    :param labels: the labels that you want to display per value. In our case we are going to use
     the request types.
    :param values: the values of each label element. In our case we are going to use the amount of
     request of each type.
    :param title: the graph title displayed in the top.
    :param portion_colors: the customized colors for each portion.
    :param show_legend: if you want to display the legend of each portion.
    :param show_values: instead of % display values for each portion.
    """
    layout = None
    if title:
        title_element = go.layout.Title(
            text=title,
            x=0.5,
            font=go.layout.title.Font(
                size=30,
                family='Arial',
                color='#797979',
            ),
        )
        layout = go.Layout(title=title_element)
    pie = {
        'labels': labels,
        'values': values,
        'marker': {'line': {'color': '#000000', 'width': 2}},
        'textfont': go.pie.Textfont(size=25, family='Arial'),
        'textposition': 'inside',
        'sort': False,
        'textinfo': 'percent+value',
    }
    if portions_colors:
        pie['marker'].update({'colors': portions_colors})

    if show_values:
        pie.update({'textinfo': 'value'})

    f = go.Figure(
        data=go.Pie(**pie),
        layout=layout,
    )

    f.update_layout(
        autosize=False,
        width=1200,
        height=800,
        showlegend=show_legend,
    )

    if show_legend:
        f.update_layout(
            legend={
                'font': {'size': 25},
                'orientation': 'h',
                'yanchor': 'top',
                'xanchor': 'center',
                'x': 0.5,
                'y': -0.3,
            },
        )

    with NamedTemporaryFile(delete=False) as file:
        f.write_image(file)
        return pathlib.Path(file.name).as_uri()


def _generate_bar_chart(x, y, x_title, y_title):
    """
    Function that generates a BAR chart using the plotly library. The styling has been preconfigured
     but could be changed.

    :param x: the x axis values, usually names. In our case will be product names.
    :param y: the y axis values, usually numbers. In our case will be product provision time avg.
    :param x_title: the x axis title. Products
    :param y_title: the y axis title. <b>Processing time (days)</b>
    """

    f = go.Figure()

    f.add_trace(
        go.Bar(
            x=x,
            y=y,
            marker_color='rgb(158,202,225)',
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5,
        ),
    )
    f.update_layout(
        bargap=0,
        showlegend=False,
        width=1200,
        height=800,
    )
    f.update_xaxes(title_text=x_title, tickangle=-90)
    max_value = max(y) if y else 0
    m = max_value * 1.25 if max_value > 0 else 1

    f.update_yaxes(
        title_text=y_title,
        range=[0, m],
    )

    with NamedTemporaryFile(delete=False) as file:
        f.write_image(file)
        return pathlib.Path(file.name).as_uri()


def _generate_vertical_bar_chart_by_type(x, traces, x_title=None, y_title=None, showlegend=True):
    """
    Function that generates a BAR chart using the plotly library. The styling has been preconfigured
     but could be changed.
    Each bar contains inside the amounts for each type. Each trace is a type.

    :param x: the x axis values, usually names. In our case will be product names.
    :param traces: the traces dict that must contain per each dict the values, the name and the
     desired color.
    :param x_title: the text that will be displayed in the x axis.
    :param y_title: the text that will be displayed in the y axis.
    :param showlegend: if we want to display the legend (true by default).
    """
    f = go.Figure()
    for trace in traces.values():
        f.add_trace(
            go.Bar(
                y=trace['values'],
                x=x,
                name=trace['name'],
                orientation='v',
                marker={
                    'color': trace['color'],
                },
            ),
        )
    f.update_layout(
        barmode='stack',
        bargap=0.5,
        showlegend=showlegend,
    )
    f.update_xaxes(title_text=x_title if x_title else 'Products')
    f.update_yaxes(title_text=y_title if y_title else 'Requests')

    with NamedTemporaryFile(delete=False) as file:
        f.write_image(file)
        return pathlib.Path(file.name).as_uri()


def _generate_map_chart(countries, values):
    """
    Function that generates a Choropleth Map chart using the plotly library. The styling has been
     preconfigured but could be changed.
    The color scale has 3 colors where red is the max, yellow -20% and green the lower.

    :param countries: a list with all relevant countries to show.
    :param values: a list with all values per each country.
    """
    simple_colorscale = [
        [0, 'rgb(173,255,47)'],
        [0.8, 'rgb(255,255,0)'],
        [1, 'rgb(255,10,10)'],
    ]
    f = go.Figure()
    f.add_trace(
        go.Choropleth(
            locationmode='country names',
            locations=countries,
            colorscale=simple_colorscale,
            z=values,
        ),
    )
    f.update_layout(
        width=1200,
        height=800,
    )
    f.update_geos(
        resolution=110,
        showcoastlines=True,
        showcountries=True,
        showlakes=False,
        showland=True,
        landcolor='royalblue',
        showocean=True,
        oceancolor='white',
    )
    with NamedTemporaryFile(delete=False) as file:
        f.write_image(file)
        return pathlib.Path(file.name).as_uri()


def _get_main_account(client):
    accounts = client.accounts.all()
    main_account = accounts[0]
    return main_account['name'], main_account['id']


def _split_chart_data(data_length):
    expected_charts = math.ceil(data_length / ELEMENTS_PER_CHART)
    if data_length == 0:
        yield Part(0, 0, 0, 0)
    else:
        for n in range(0, expected_charts):
            start_range = n * ELEMENTS_PER_CHART
            end_range = min(data_length, (n + 1) * ELEMENTS_PER_CHART)
            yield Part(start_range, end_range, int(n + 1), expected_charts)


def _generate_pie_chart_from_datat(client, parameters):
    r, total = _get_request_count_group_by_type(client, parameters)
    return _generate_pie_chart(
        labels=list(r.keys()),
        values=list(r.values()),
        show_legend=True,
    ), total


def _generate_bar_charts_from_data(report_data, x_title):
    final_result = _calculate_the_average_and_sort(report_data)
    x = []
    y = []
    for value in final_result.values():
        if value['avg'] >= THRESHOLD:
            x.append(value['name'])
            y.append(value['avg'])
    charts = []
    parts = _split_chart_data(len(x))
    for part in parts:
        charts.append(
            _generate_bar_chart(
                x=x[part.start_index:part.end_index],
                y=y[part.start_index:part.end_index],
                x_title=f'{x_title} (chart {part.part} of {part.total})',
                y_title='Processing time (days)',
            ),
        )
    return charts


def _generate_vertical_bar_charts_per_type_from_data(report_data):
    x = []
    traces = {
        'cancel': {'values': [], 'name': 'Cancel', 'color': 'red'},
        'adjustment': {'values': [], 'name': 'Adjustment', 'color': 'yellow'},
        'purchase': {'values': [], 'name': 'Purchase', 'color': 'purple'},
        'change': {'values': [], 'name': 'Change', 'color': 'blue'},
        'suspend': {'values': [], 'name': 'Suspend', 'color': 'green'},
        'resume': {'values': [], 'name': 'Resume', 'color': 'gray'},
    }
    charts = []
    data_length = len(list(report_data['product'].keys()))
    parts = _split_chart_data(data_length)

    ordered_report_data = dict(
        sorted(
            report_data['product'].items(),
            key=lambda d: d[1]['amount_per_type']['total'],
            reverse=True,
        ),
    )

    for part in parts:
        x = []
        partial_traces = copy.deepcopy(traces)
        for product in list(ordered_report_data.values())[part.start_index:part.end_index]:
            x.append(product['name'])
            for t in ('cancel', 'adjustment', 'purchase', 'change', 'suspend', 'resume'):
                partial_traces[t]['values'].append(product['amount_per_type'][t])
        charts.append(
            _generate_vertical_bar_chart_by_type(
                x=x,
                traces=partial_traces,
                x_title=f'Products (chart {part.part} of {part.total})',
            ),
        )
    return charts


def _generate_choropleth_map_and_table_from_data(report_data):
    countries = list(report_data['country'].keys())
    values = [element['amount'] for element in list(report_data['country'].values())]
    chart = _generate_map_chart(countries, values)

    result = {}
    for row in zip(countries, values):
        result[row[0]] = row[1]
    ordered_result = dict(sorted(result.items(), key=lambda d: d[1], reverse=True))

    table = []
    n = 1
    for country, amount in ordered_result.items():
        table.append({'number': n, 'country': country.capitalize(), 'amount': amount})
        n += 1
    return chart, table


def _process_vendor_data(report_data, request):
    vendor_id = get_value(request['asset']['connection'], 'vendor', 'id')
    vendor = report_data['vendor'].get(
        vendor_id,
        {
            'name': get_value(request['asset']['connection'], 'vendor', 'name'),
            'data': [],
            'provision_times': [],
            'amount_per_type': {
                'cancel': 0,
                'adjustment': 0,
                'purchase': 0,
                'change': 0,
                'suspend': 0,
                'resume': 0,
                'total': 0,
            },
        },
    )
    vendor['amount_per_type'][request['type']] += 1
    vendor['amount_per_type']['total'] += 1
    vendor['provision_times'].append(request['provision_time'])
    report_data['vendor'][vendor_id] = vendor


def _process_product_data(report_data, request):
    product_id = request['asset']['product']['id']
    product = report_data['product'].get(
        product_id,
        {
            'name': request['asset']['product']['name'],
            'data': [],
            'provision_times': [],
            'amount_per_type': {
                'cancel': 0,
                'adjustment': 0,
                'purchase': 0,
                'change': 0,
                'suspend': 0,
                'resume': 0,
                'total': 0,
            },
        },
    )
    product['amount_per_type'][request['type']] += 1
    product['amount_per_type']['total'] += 1
    product['provision_times'].append(request['provision_time'])
    report_data['product'][product_id] = product


def _process_country_data(report_data, request):
    country = get_dict_element(request, 'asset', 'tiers', 'customer', 'contact_info', 'country')
    if country:
        country_name = COUNTRIES[country.upper()]

        country_data = report_data['country'].get(
            country_name,
            {'amount': 0},
        )
        country_data['amount'] += 1
        report_data['country'][country_name] = country_data


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context=None,
):
    requests = _get_requests(client, parameters)

    report_data = {
        'product': {},
        'vendor': {},
        'country': {},
    }
    progress = 0
    total = requests.count()
    for request in requests:
        request['provision_time'] = (
            convert_to_datetime(request.get('updated'))
            - convert_to_datetime(request.get('created'))
        ).days
        _process_vendor_data(report_data, request)
        _process_product_data(report_data, request)
        _process_country_data(report_data, request)
        progress += 1
        progress_callback(progress, total)

    pdf_reports = {'charts': []}

    chart, total = _generate_pie_chart_from_datat(client, parameters)
    pdf_reports['charts'].append(
        {
            'title': '1. Distribution of requests per type',
            'description':
                'Total amount of requests within the period from '
                f"{parameters['date']['after'].split('T')[0]} to "
                f"{parameters['date']['before'].split('T')[0]} : "
                f"<b>{total}<b>.",
            'images': [chart],
        },
    )

    chart, table = _generate_choropleth_map_and_table_from_data(report_data)
    pdf_reports['charts'].append(
        {
            'title': '2. Requests per country',
            'description':
                'Following charts represents the request amount per country.'
                ' The countries that have more than the 20% are near red.',
            'table': table,
            'images': [chart],
        },
    )

    charts = _generate_vertical_bar_charts_per_type_from_data(report_data)
    pdf_reports['charts'].append(
        {
            'title': '3. Requests per product per type',
            'description':
                'Following charts represents the request amount per product.'
                ' Bar contains the distribution of requests per type.',
            'images': charts,
        },
    )

    charts = _generate_bar_charts_from_data(report_data['vendor'], 'Vendors')
    pdf_reports['charts'].append(
        {
            'title': '4. Averge Request Processing time (per vendor)',
            'description':
                'Following charts represents the average processing time of requests per vendor.',
            'images': charts,
        },
    )

    charts = _generate_bar_charts_from_data(report_data['product'], 'Products')
    pdf_reports['charts'].append(
        {
            'title': '5. Averge Request Processing time (per product)',
            'description':
                'Following charts represents the average processing time of requests per product.'
                ' Bar contains the distribution of requests per type.',
            'images': charts,
        },
    )

    account_name, account_id = _get_main_account(client)
    pdf_reports['range'] = {
        'start': parameters['date']['after'].split('T')[0],
        'end': parameters['date']['before'].split('T')[0],
    }
    pdf_reports['generation_date'] = date.today().strftime('%B %d, %Y')

    return pdf_reports
