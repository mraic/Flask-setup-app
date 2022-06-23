from marshmallow import fields, ValidationError
from marshmallow.validate import Length
from marshmallow_enum import EnumField

from src import Property
from src.views import BaseSchema

def validate_price(price):
    if price < 0:
        raise ValidationError('Price must be greater than 0')

def validate_living_area(living_area):
    if living_area < 0:
        raise ValidationError('Living area must be greater than 0')

class PropertySchema(BaseSchema):
    id = fields.UUID(dump_only = True)
    address = fields.Str(required=True, validate=Length(min=5, max=50))
    price = fields.Float(required=True, validate=validate_price)
    living_area = fields.Float(required=True, validate=validate_living_area)
    owner_id = fields.UUID(required=True)
    status = EnumField(Property.STATUSES, by_value=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class PropertyWithTotalSchema(PropertySchema):
    total = fields.Int()

class PropertyResponseOneSchema(BaseSchema):
    data = fields.Nested("PropertySchema", dump_only=True)
    message = fields.String(dump_only=True)

#autocomplete schema
class PropertyResponseManySchema(BaseSchema):
    data = fields.Nested("PropertySchema", many = True, dump_only=True)
    message = fields.String(dump_only=True)

class ActivateDeactivatePropertySchema(BaseSchema):
    status = EnumField(Property.STATUSES, by_value=True, dump_only=True)
    message = fields.String(dump_only=True)

class RequestFilterPropertySchema(BaseSchema):
    filter_data = fields.Nested("PropertyFilterSchema", required=False)
    paginate_data = fields.Nested("PaginationSchema", required=False)

class GetAllPropertyPaginateDataSchema(BaseSchema):
    items = fields.Nested("PropertySchema", many=True, dump_only=True)
    total = fields.Int(dump_only=True)

class GetAllPropertyPaginateSchema(BaseSchema):
    data = fields.Nested("GetAllPropertyPaginateDataSchema", dump_only=True)
    message = fields.String(dump_only=True)

class PropertyFilterSchema(BaseSchema):
    address = fields.Nested("OperatorSchema", required=False)
    price = fields.Nested("FromToSchema", required=False)
    living_area = fields.Nested("FromToSchema", required=False)

class UpdatePropertySchema(PropertySchema):
    class Meta:
        items = fields.Nested("PropertySchema", dump_only=True)
        message = fields.String(dump_only=True)
        address = fields.Str(required=True, validate=Length(min=5, max=50))
        price = fields.Float(required=True, validate=validate_price)
        living_area = fields.Float(required=True, validate=validate_living_area)
        owner_id = fields.UUID(required=True)



create_schema = PropertySchema()
response_one_property_schema = PropertyResponseOneSchema()
activate_deactivate_schema = ActivateDeactivatePropertySchema()
update_property_schema = UpdatePropertySchema()
request_property_filter_schema = RequestFilterPropertySchema()
get_all_properties_schema = GetAllPropertyPaginateSchema()
property_response_many_schema = PropertyResponseManySchema()