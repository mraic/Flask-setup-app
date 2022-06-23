from datetime import datetime

import jwt
from flask import request, current_app
from flask_apispec import doc, use_kwargs, marshal_with
from src import bpp, Activity
from src.domain import ActivityService
from src.general import security_params
from src.views import message_response_schema
from src.views.activity_schema import request_activity_filter_schema, \
     get_all_activity_schema, activity_schema, \
     get_all_activity_paginate_data_schema


@doc(description='Create activity route',
     params = security_params, tags=['Activity'])
@bpp.post('/activities')
@use_kwargs(activity_schema, apply=True)
@marshal_with(get_all_activity_paginate_data_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def create(**kwargs):

     activities_service = ActivityService(
          activity=Activity(
               user_id = kwargs.get('user_id'),
               duration = kwargs.get('duration'),
               path = kwargs.get('path')
          )
     )

     status = activities_service.create()

     return dict(message = status.message, data = activities_service.activity)

@doc(description='Activity pagination route',
     params = security_params, tags = ['Activity'])
@bpp.post('/activities/paginate')
@use_kwargs(request_activity_filter_schema, apply=True)
@marshal_with(get_all_activity_schema,200, apply = True)
@marshal_with(message_response_schema, 400, apply = True)
def activity_paginate(**kwargs):

     token = request.environ.get('HTTP_AUTHORIZATION', None)

     payload = jwt.decode(
          token,
          current_app.config.get('JWT_SECRET_KEY'),
          algorithms=['HS256']
     )

     start_time = datetime.utcnow()

     filter_data = kwargs.get('filter_data')
     paginate_data = kwargs.get('paginate_data')

     items, total, status = ActivityService.get_all_activities(
          filter_data=filter_data, paginate_data=paginate_data
     )

     stop_time = datetime.utcnow()

     activity_service = ActivityService(
          activity=Activity(
               duration = stop_time - start_time,
               path = request.path + '-->' + request.method,
               user_id=payload['id']
          )
     )
     activity_service.create()

     return dict(data=dict(items = items, total = total),
                 status = status.message)


