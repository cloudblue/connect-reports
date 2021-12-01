from copy import deepcopy

from reports.products_catalog.entrypoint import generate
from unittest.mock import MagicMock


def test_generate(
    progress,
    client_factory,
    response_factory,
    account_response,
    service_agreement_response,
    mkp_list,
    catalog_response,
):
    responses = []
    responses.append(
        response_factory(
            value=[account_response],
        ),
    )
    own_service_agreement = deepcopy(service_agreement_response)
    own_service_agreement['owner']['id'] = account_response['id']
    responses.append(
        response_factory(
            query='eq(type,service)',
            value=[service_agreement_response, own_service_agreement],
        ),
    )
    responses.append(
        response_factory(
            value=catalog_response,
        ),
    )
    responses.append(
        response_factory(
            value=mkp_list,
        ),
    )
    own_catalog = deepcopy(catalog_response)
    own_product = deepcopy(own_catalog[0])
    own_product['id'] = 'MY_PROD'
    own_catalog.append(own_product)
    responses.append(
        response_factory(
            value=own_catalog,
        ),
    )

    client = client_factory(responses)

    result = generate(client, None, progress, renderer_type='pdf', extra_context=MagicMock())

    assert len(result) == 1
    assert result[0]['id'] == 'PRD-768-002-669'
