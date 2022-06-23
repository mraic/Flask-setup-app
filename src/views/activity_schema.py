from marshmallow import fields
from marshmallow.validate import Length
from marshmallow_enum import EnumField

from .. import Activity
from ..views import BaseSchema


class ActivitySchema(BaseSchema):
    id = fields.UUID(dump_only=True)
    duration = fields.Time(required=True)
    path = fields.Str(validate=Length(min=2, max=100))
    user_id = fields.UUID(required=True)
    status = EnumField(Activity.STATUSES, by_value=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ActivityFullSchema(ActivitySchema):
    user = fields.Nested("UserSchema")

class ActivityFilterSchema(BaseSchema):
    path = fields.Nested("OperatorSchema", required=False)
    user_id = fields.UUID(required=False)

class ActivityFilterRequestSchema(BaseSchema):
    filter_data = fields.Nested('ActivityFilterSchema', required=False)
    paginate_data = fields.Nested('PaginationSchema', required=False)

class GetAllActivityPaginateDataSchema(BaseSchema):
    items = fields.Nested("ActivityFullSchema", many=True, dump_only=True)
    total = fields.Int(dump_only=True)
    
class GetAllActivityPaginateSchema(BaseSchema):
    data = fields.Nested("GetAllActivityPaginateDataSchema", dump_only=True)
    message = fields.String(dump_only=True)



activity_schema = ActivitySchema()
get_all_activity_paginate_data_schema = GetAllActivityPaginateDataSchema()
get_all_activity_schema = GetAllActivityPaginateSchema()
request_activity_filter_schema = ActivityFilterRequestSchema()