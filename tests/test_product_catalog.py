from reports.products_catalog.entrypoint import generate
from unittest.mock import MagicMock


def test_generate(progress, client_factory, response_factory, catalog_response):
    responses = []
    responses.append(
        response_factory(
            count=1,
        ),
    )

    responses.append(
        response_factory(
            query='and(eq(visibility.catalog,true),eq(status,published))',
            value=catalog_response,
        ),
    )

    client = client_factory(responses)

    result = generate(client, None, progress, renderer_type='pdf', extra_context=MagicMock())

    assert result == catalog_response
