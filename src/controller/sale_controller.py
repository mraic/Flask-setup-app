from flask_apispec import use_kwargs, doc, marshal_with

from src import bpp, Sale
from src.domain import SaleService
from ..views import \
    sale_response_one_schema, update_sale_schema, create_sale_schema, \
    message_response_schema, delete_schema, get_all_sales_paginate_schema, \
    request_sale_filter_schema


@doc(description='Sale Route', tags=['Sales'])
@bpp.post('/sales')
@use_kwargs(create_sale_schema, apply=True)
@marshal_with(sale_response_one_schema, 200, apply=True)
@marshal_with(message_response_schema,400, apply=True)
def create_sale(**kwargs):

    sale_service = SaleService(
        sale=Sale(
            buyer_id = kwargs.get('buyer_id'),
            property_id = kwargs.get('property_id')
        )
    )

    status = sale_service.create()

    return dict(message=status.message,  data = sale_service.sale)

@doc(description='Sale Alter Route', tags=['Sales'])
@bpp.put('/sales/<uuid:sale_id>')
@use_kwargs(update_sale_schema, apply=True)
@marshal_with(sale_response_one_schema,apply=True)
@marshal_with(message_response_schema,400 ,apply=True)
def alter_sale(**kwargs):

    sale_service = SaleService(
        sale=Sale(
            buyer_id = kwargs.get('buyer_id'),
            property_id = kwargs.get('property_id')
        )
    )

    status = sale_service.alter()

    return dict(message = status.message, data= sale_service.sale)

@doc(description='Sale Delete Route', tags=['Sales'])
@bpp.delete('/sales/delete/<uuid:sale_id>')
@use_kwargs(delete_schema, apply=True)
@marshal_with(sale_response_one_schema,200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def delete_sale(**kwargs):

    sale_service = SaleService(sale=Sale(id=kwargs.get('id')))

    status = sale_service.delete(_id=sale_service.sale.id)

    return dict(message=status.message, data=sale_service.sale)


@doc(description='Sale Pagination Route', tags =['Sales'])
@bpp.post('/sales/paginate')
@use_kwargs(request_sale_filter_schema, apply=True)
@marshal_with(get_all_sales_paginate_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def paginate_sale(**kwargs):

    filter_data=kwargs.get('filter_data')
    paginate_data=kwargs.get('paginate_data')

    items, total, status = SaleService.get_all_sales(
        filter_data=filter_data, paginate_data=paginate_data
    )

    return dict(data=dict(items=items, total=total),
                status = status.message)