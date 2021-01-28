from reports.usage_in_subscription.entrypoint import generate


def test_generate_usage(
        progress,
        client_factory,
        response_factory,
        usage_records_response,
        ff_request,
):

    responses = []

    asset = ff_request['asset']

    parameters = {
        "period": {
            "after": "2020-12-01T00:00:00",
            "before": "2021-01-01T00:00:00"
        },
        "product": ["PRD-1"],
    }

    responses.append(
        response_factory(
            count=1
        )
    )

    responses.append(
        response_factory(
            query='and(in(product.id,(PRD-1)),eq(status,active))',
            value=[asset]
        )
    )

    responses.append(
        response_factory(
            query='and(eq(asset.id,AS-1895-0864-1238),in(status,(approved,closed)),or(and(ge('
                  'start_date,2020-12-01T00:00:00),lt(start_date,2021-01-01T00:00:00)),'
                  'and(ge(end_date,2020-12-01T00:00:00),lt(end_date,2021-01-01T00:00:00)),'
                  'and(lt(start_date,2020-12-01T00:00:00),gt(end_date,2021-01-01T00:00:00))))',
            value=[usage_records_response]
        )
    )

    client = client_factory(responses)

    result = list(generate(client, parameters, progress))

    assert len(result) == 1
    for res in result:
        assert res != ''
