from datetime import datetime, timedelta

import jwt
from flask import request, current_app, jsonify
from flask_apispec import doc, marshal_with, use_kwargs

from ..domain import ActivityService
from ..general import password_reset_email

from . import bpp
from .. import User, AppLogException, Activity
from ..domain.user_service import UserService
from ..general import security_params, allow_access, send_email, Status
from ..views import message_response_schema, request_create, \
    response_one_user_schema, login_user, response_login_schema, \
    get_all_users_schema, request_user_filter_schema, \
    update_user_schema, reset_user_password_schema, ResetUserPasswordByIdSchema, \
    send_reset_password_email, auto_complete_schema, response_many_user_schema


@doc(description='User Route', tags=['Users'])
@bpp.post('/users')

@use_kwargs(request_create, apply=True)
@marshal_with(response_one_user_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def create_user(**kwargs):

    user_service = UserService(
        user=User(
            username=kwargs.get('username'),
            first_name=kwargs.get('first_name'),
            last_name=kwargs.get('last_name'),
            email=kwargs.get('email'),
            password=kwargs.get('password')))

    status = user_service.create()
    return dict(message=status.message, data=user_service.user)


@doc(description = "User activate route", tags=['Users'])
@bpp.put('/users/activate/<uuid:user_id>')
#allow_access
@marshal_with(response_one_user_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def activate_user(user_id):

    # token = request.environ.get('HTTP_AUTHORIZATION', None)
    # payload = jwt.decode(
    #     token,
    #     current_app.config.get('JWT_SECRET_KEY'),
    #     algorithms=["HS256"])

    start_time = datetime.utcnow()
    user_service = UserService(user=User(id=user_id))

    stop_time = datetime.utcnow()

    # activity_service = ActivityService(
    #     activity=Activity(
    #         duration=stop_time - start_time,
    #         path=request.path,
    #         user_id=payload['token']
    #     )
    # )

    status = user_service.activate()
    #activity_service.create()
    return dict(message=status.message, data=user_service.user)

@doc(description = "User deactivate route",
     params = security_params, tags=['Users'])
@bpp.delete('/users/<uuid:user_id>')
@allow_access
@marshal_with(response_one_user_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def deactivate_user(user_id):
    start_time = datetime.utcnow()

    token = request.environ.get('HTTP_AUTHORIZATION', None)
    payload = jwt.decode(
        token,
        current_app.config.get('JWT_SECRET_KEY'),
        algorithms=["HS256"])

    user_service = UserService(user=User(id=user_id))
    status = user_service.deactivate(current_user_id=payload['id'])

    stop_time = datetime.utcnow()

    activity_service = ActivityService(
        activity=Activity(
            duration=stop_time - start_time,
            path=request.path + '-->' + request.method,
            user_id=user_id
        )
    )

    activity_service.create()
    return dict(message=status.message, data=user_service.user)


@doc(description = "User activate route", tags=['Users'])
@bpp.post('/login/staticMethod')
#allow_access
@use_kwargs(login_user, apply=True)
@marshal_with(response_login_schema, 200, apply=False)
@marshal_with(message_response_schema, 400, apply=True)
def user_login_static_method(**kwargs):
    start_time = datetime.utcnow()

    token = request.environ.get('HTTP_AUTHORIZATION', None)
    payload = jwt.decode(
        token,
        current_app.config.get('JWT_SECRET_KEY'),
        algorithms=["HS256"]
    )

    user_service_dict, message = UserService.login_user(
        username=kwargs.get('username'),
        password=kwargs.get('password'))

    stop_time = datetime.utcnow()

    activity_service = ActivityService(
        activity=Activity(
            duration = stop_time - start_time,
            path = request.path + '-->' + request.method,
            user_id = payload['id']
        )
    )

    activity_service.create()

    return dict(message=message.message, data=user_service_dict)

@doc(description = "User login route", tags=['Users'])
@bpp.post('/login')
@use_kwargs(login_user, apply=True)
@marshal_with(response_login_schema, 200, apply=False)
@marshal_with(message_response_schema, 400, apply=True)
def user_login(**kwargs):
    start_time = datetime.utcnow()
    user_service = UserService(
        user=User(
            username=kwargs.get('username'),
            password=kwargs.get('password')))

    stop_time = datetime.utcnow()

    message, data = user_service.login()

    activity_service = ActivityService(
        activity=Activity(
            duration=stop_time - start_time,
            path=request.path + '-->' + request.method,
            user_id=user_service.user.id
        )
    )
    activity_service.create()
    return dict(message=message.message, data=data)


@doc(description = "Get all users", params=security_params, tags = ["Users"])
@bpp.post('/users/paginate')
#@allow_access
@use_kwargs(request_user_filter_schema, apply=True)
@marshal_with(get_all_users_schema, 200, apply=False)
@marshal_with(message_response_schema, 400, apply = True)
def get_users(**kwargs):

    filter_data = kwargs.get('filter_data')
    paginate_data = kwargs.get('paginate_data')

    items, total, status = UserService.get_all_users(
        filter_data=filter_data, paginate_data=paginate_data)

    return dict(data=dict(items=items, total=total),
                status=status.message)


@doc(description = "Update users information", tags = ['Users'])
@bpp.put('/users/<uuid:user_id>')
@use_kwargs(update_user_schema, apply = True)
@marshal_with(response_one_user_schema, 200, apply = True)
@marshal_with(message_response_schema, 400, apply = True)
def update_user(user_id, **kwargs):
    start_time = datetime.utcnow()

    user_service = UserService(
        user = User(
            id=user_id,
            email = kwargs.get('email'),
            first_name = kwargs.get('first_name'),
            last_name = kwargs.get('last_name'),
            username = kwargs.get('username')
        )
    )
    stop_time = datetime.utcnow()

    status = user_service.alter()

    activity_service = ActivityService(
        activity=Activity(
            duration=stop_time - start_time,
            path=request.path + '-->' + request.method,
            user_id=user_id
        )
    )
    activity_service.create()
    return dict(message = status.message, data = user_service.user)

@doc(description = "Change or reset password",
     params=security_params,tags = ['Users'])
@bpp.put('/users/changeMyPassword')
@allow_access
@use_kwargs(reset_user_password_schema, apply=True)
@marshal_with(response_one_user_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply = True)
def reset_password(**kwargs):

    token = request.environ.get('HTTP_AUTHORIZATION', None)
    payload = jwt.decode(
        token,
        current_app.config.get('JWT_SECRET_KEY'),
        algorithms=["HS256"])

    user_service = UserService(
        user=User(
            id=payload['id'],
            password=kwargs.get('old_password'),
        ))

    start_time = datetime.utcnow()

    status = user_service.reset_password(
        new_password=kwargs.get('new_password'))

    stop_time = datetime.utcnow()

    activity_service = ActivityService(
        activity=Activity(
            duration=stop_time - start_time,
            path=request.path + '-->' + request.method,
            user_id=payload['id']
        )
    )
    activity_service.create()
    return dict(message=status.message, data=user_service.user)


@doc(description = "Reset password by role", tags = ['Users'])
@bpp.put('/users/changePassword/<uuid:user_id>')
#@allow_access
@use_kwargs(ResetUserPasswordByIdSchema, apply=True)
@marshal_with(response_one_user_schema, 200, apply = True)
@marshal_with(message_response_schema, 400, apply = True)
def reset_password_id(user_id,**kwargs):

    start_time = datetime.utcnow()

    user_service = UserService(
        user=User(
            id = user_id,
            password = kwargs.get('old_password'),
        )
    )

    status = user_service.reset_password_by_id(
        _id = user_id,
        new_password=kwargs.get('new_password'),
        confirm_new_password = kwargs.get('confirm_new_password')
    )

    stop_time = datetime.utcnow()

    activity_service = ActivityService(
        activity=Activity(
            duration = stop_time - start_time,
            path = request.path + '-->' + request.method,
            user_id = User.id
        )
    )

    activity_service.create()
    return dict(message= status.message, data = user_service.user)


@doc(description = "Reset password by role", tags = ['Users'])
@bpp.post('/users/sendResetPasswordLink')
@use_kwargs(send_reset_password_email, apply=True)
@marshal_with(send_reset_password_email, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def send_reset_password_link(email):
    my_json = request.get_json()
    if my_json[email] is None:
        raise AppLogException(Status.mail_cannot_be_empty())

    data = UserService.get_one_by_email(my_json[email])
    if data.user is None:
        raise AppLogException(Status.user_not_activated())


    token = jwt.encode({'user_id': str(data.user.id),
                         'exp': datetime.utcnow() + timedelta(minutes=15)},
                        current_app.config.get('SECRET_KEY')).decode('UTF-8')

    link_token = "{0}/reset-password/{1}".format(
        current_app.config.get('FLASK_SETUP_APP_FRONTEND_API'), token)
    link_login = "{0}/login".format(
        current_app.config.get('FLASK_SETUP_APP_FRONTEND_API'))
    html = password_reset_email(link_login, link_token)
    send_email({
        "subject": "Test app password reset link",
        "body": html,
        "recipient": data.user.email
    })

    return jsonify(
        dict(status=Status.successfully_processed())
    )

@doc(description = "Autocomplete for users", tags = ['Users'])
@bpp.post('/users/autocomplete')
@use_kwargs(auto_complete_schema, apply=True)
@marshal_with(response_many_user_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def autocomplete(**kwargs):

    data , status = UserService.autocomplete(search=kwargs.get('search'))

    return dict(data = data, message=status.message)


