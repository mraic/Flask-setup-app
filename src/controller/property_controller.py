from datetime import datetime

import jwt
from flask import request, current_app
from flask_apispec import marshal_with, use_kwargs, doc

from src import Property, bpp, Activity
from src.domain import ActivityService
from src.domain.property_service import PropertyService
from src.general import status, security_params
from src.views import message_response_schema
from src.views.property_schema import create_schema, \
    response_one_property_schema, update_property_schema, \
    activate_deactivate_schema, request_property_filter_schema, \
    get_all_properties_schema


@doc(description='Create Property Route',
    params = security_params, tags=['Property'])
@bpp.post('/properties')
@use_kwargs(create_schema, apply=True)
@marshal_with(response_one_property_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def property_create(**kwargs):

    token = request.environ.get('HTTP_AUTHORIZATION', None)
    payload = jwt.decode(
        token,
        current_app.config.get('JWT_SECRET_KEY'),
        algorithms=["HS256"])

    start_time = datetime.utcnow()
    property_service = PropertyService(
        property=Property(
            owner_id = kwargs.get('owner_id'),
            address = kwargs.get('address'),
            price = kwargs.get('price'),
            living_area = kwargs.get('living_area')
        )
    )

    status = property_service.create()

    stop_time = datetime.utcnow()

    activity_service = ActivityService(
        activity=Activity(
            duration=stop_time - start_time,
            path=request.path + '-->' + request.method,
            user_id=payload['id']
        )
    )

    activity_service.create()

    return dict(message = status.message, data = property_service.property)

@doc(description = 'Update Property informations',
     params = security_params, tags = ['Property'])
@bpp.put('/properties/<uuid:property_id>')
@use_kwargs(update_property_schema, apply = True)
@marshal_with(response_one_property_schema,apply=True)
@marshal_with(message_response_schema, 400, apply = True)
def property_alter(property_id, **kwargs):

    token = request.environ.get('HTTP_AUTHORIZATION', None)
    payload=jwt.decode(
        token,
        current_app.config.get('JWT_SECRET_KEY'),
        algorithms=['HS256']
    )

    start_time = datetime.utcnow()

    property_service = PropertyService(
        property=Property(
            id = property_id,
            address = kwargs.get('address'),
            living_area = kwargs.get('living_area'),
            owner_id = kwargs.get('owner_id'),
            price =kwargs.get('price')
        )
    )
    stop_time = datetime.utcnow()

    status = property_service.alter()

    activity_service = ActivityService(
        activity=Activity(
            duration=stop_time - start_time,
            path=request.path + '-->' + request.method,
            user_id=payload['id']
        )
    )

    activity_service.create()

    return dict(message=status.message, data = property_service.property)

@doc(description = 'Deactivate property', tags = ['Property'])
@bpp.delete('/properties/deactivate/<uuid:property_id>')
@marshal_with(activate_deactivate_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def property_deactivate(property_id):

    # token = request.environ.get('HTTP_AUTHORIZATION', None)
    # payload = jwt.decode(
    #     token,
    #     current_app.config.get('JWT_SECRET_KEY'),
    #     algorithms=["HS256"]
    # )
    start_time = datetime.utcnow()

    property_service = PropertyService(property=Property(id = property_id))

    stop_time = datetime.utcnow()

    status = property_service.deactivate(_id = property_id)

    # activity_service = ActivityService(
    #     activity=Activity(
    #         duration=stop_time - start_time,
    #         path=request.path + '-->' + request.method,
    #         user_id=payload['id']
    #     )
    # )

    #activity_service.create()

    return dict(message = status.message, data = property_service)

@doc(description = 'Deactivate property', tags = ['Property'])
@bpp.post('/properties/activate/<uuid:property_id>')
@marshal_with(activate_deactivate_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def property_activate(property_id):

    # token = request.environ.get('HTTP_AUTHORIZATION', None)
    # payload = jwt.decode(
    #     token,
    #     current_app.config.get('JWT_SECRET_KEY'),
    #     algorithms=["HS256"]
    # )
    start_time = datetime.utcnow()

    property_service = PropertyService(property=Property(id = property_id))

    stop_time = datetime.utcnow()

    status = property_service.activate(_id = property_id)

    # activity_service = ActivityService(
    #     activity=Activity(
    #         duration=stop_time - start_time,
    #         path=request.path + '-->' + request.method,
    #         user_id=payload['id']
    #     )
    # )

    #activity_service.create()

    return dict(message = status.message, data = property_service)


@doc(description='Pagination for Properties', tags = ['Property'])
@bpp.post('/properties/paginate')
@use_kwargs(request_property_filter_schema, apply=True)
@marshal_with(get_all_properties_schema,200, apply = True)
@marshal_with(message_response_schema, 400, apply = True)
def property_pagination(**kwargs):

    filter_data = kwargs.get('filter_data')
    paginate_data = kwargs.get('paginate_data')

    items, total, status = PropertyService.get_all_properties(
        filter_data=filter_data, paginate_data=paginate_data
    )

    return dict(data=dict(items=items, total=total),
                status=status.message)