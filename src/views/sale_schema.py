from marshmallow import fields

from src.views import BaseSchema

class SaleSchema(BaseSchema):
    id = fields.UUID(dump_only=True)
    buyer_id = fields.UUID(required=True)
    property_id = fields.UUID(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class SalesFullSchema(SaleSchema):
    user = fields.Nested('UserSchema', dump_only=True)
    properties = fields.Nested('PropertySchema', dump_only=True)

class SaleTotalSchema(SaleSchema):
    total = fields.Int()

class SaleResponseOneSchema(BaseSchema):
    data = fields.Nested("SaleSchema", dump_only = True)
    message = fields.String(dump_only = True)

class UpdateSaleSchema(SaleSchema):
    class Meta:
        items = fields.Nested("BaseSchema", dump_only=True)
        message = fields.String(dump_only=True)
        fields = ('buyer_id', 'property_id')

class DeleteSchema(BaseSchema):
    id = fields.UUID(required=True)

class GetAllSalesPaginateDataSchema(BaseSchema):
    items = fields.Nested("SalesFullSchema", many = True, dump_only=True)
    total = fields.Int(dump_only=True)

class GetAllSalesPaginateSchema(BaseSchema):
    data = fields.Nested("GetAllSalesPaginateDataSchema", dump_only=True)
    message = fields.String(dump_only=True)

class SaleFilterRequestSchema(BaseSchema):
    user = fields.Nested("UserFilterSchema", required=False)

class RequestFilterSaleSchema(BaseSchema):
    filter_data = fields.Nested("SaleFilterRequestSchema", required=False)
    paginate_data = fields.Nested("PaginationSchema", required=False)

create_sale_schema = SaleSchema()
sale_response_one_schema = SaleResponseOneSchema()
update_sale_schema = UpdateSaleSchema()
delete_schema = DeleteSchema()
get_all_sales_paginate_schema = GetAllSalesPaginateSchema()
request_sale_filter_schema =RequestFilterSaleSchema()