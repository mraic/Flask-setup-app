from marshmallow import fields
from marshmallow.validate import Length
from marshmallow_enum import EnumField

from . import Hellper
from .. import User
from ..views import BaseSchema


class UserSchema(BaseSchema):
    id = fields.UUID(dump_only=True)
    username = fields.Str(required=True, validate=Length(min=5, max=50))
    first_name = fields.Str(required=True, validate=Length(min=5, max=50))
    last_name = fields.Str(required=True, validate=Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True, validate=Length(min=5, max=50), load_only=True)
    status = EnumField(User.STATUSES, by_value=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class UserLoginJWTSchema(UserSchema):
    access_token = fields.Str(dump_only=True)


class UserWithTotalSchema(UserSchema):
    total_ = fields.Int()

class LoginSchema(UserSchema):
    class Meta:
        datetimeformat = Hellper.datetime_format
        dateformat = Hellper.date_format
        fields = ('username', 'password')

class UserResponseOneSchema(BaseSchema):
    data = fields.Nested("UserSchema", dump_only=True)
    message = fields.String(dump_only=True)

class UserResponseManySchema(BaseSchema):
    data = fields.Nested("UserSchema", many=True, dump_only=True)
    message = fields.String(dump_only=True)

class UserLoginResponseSchema(BaseSchema):
    data = fields.Nested("UserLoginJWTSchema", dump_only=True)
    message = fields.String(dump_only=True)

class GetAllUsersPaginateDataSchema(BaseSchema):
    items = fields.Nested("UserWithTotalSchema", many=True, dump_only=True)
    total = fields.Int(dump_only=True)

class GetAllUsersPaginateSchema(BaseSchema):
    data = fields.Nested("GetAllUsersPaginateDataSchema", dump_only=True)
    message = fields.String(dump_only=True)

class UserFilterSchema(BaseSchema):
    username = fields.Nested("OperatorSchema", required=False)
    first_name = fields.Nested("OperatorSchema", required=False)
    last_name = fields.Nested("OperatorSchema", required=False)
    email = fields.Nested("OperatorSchema", required=False)

class UserFilterRequestSchema(BaseSchema):
    filter_data = fields.Nested("UserFilterSchema", required=False)
    paginate_data = fields.Nested("PaginationSchema", required=False)

class UpdateUserSchema(UserSchema):
    class Meta:
        items = fields.Nested("UserSchema", dump_only=True)
        message = fields.String(dump_only=True)
        fields = ('username', 'email','first_name','last_name')

class ResetUserPasswordSchema(BaseSchema):
    old_password = fields.Str(
        required=True, validate=Length(max=50), load_only=True)

    new_password = fields.Str(
        required=True, validate=Length(min=5, max=50), load_only=True)

class ResetUserPasswordByIdSchema(BaseSchema):
    old_password = fields.Str(
        required=True, validate=Length(max=50), load_only=True)

    new_password = fields.Str(
        required=True, validate=Length(min=5, max=50), load_only=True)

    confirm_new_password = fields.Str(
        required=True, validate=Length(min = 5, max = 50), load_only=True
    )

class SendResetPasswordEmail(BaseSchema):
    email = fields.Email(required=True, load_only= True)

class AutoCompleteSchema(BaseSchema):
    search = fields.String(required=True)




login_user = LoginSchema()
request_create = UserSchema()
response_one_user_schema = UserResponseOneSchema()
response_login_schema = UserLoginResponseSchema()
request_user_filter_schema = UserFilterRequestSchema()
get_all_users_schema = GetAllUsersPaginateSchema()
update_user_schema = UpdateUserSchema()
reset_user_password_schema = ResetUserPasswordSchema()
reset_user_password_by_id_schema = ResetUserPasswordByIdSchema()
send_reset_password_email = SendResetPasswordEmail()
auto_complete_schema = AutoCompleteSchema()
response_many_user_schema = UserResponseManySchema()