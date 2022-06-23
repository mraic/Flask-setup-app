from sqlalchemy import and_

from . import UserService
from .. import Activity, AppLogException, User
from ..general import Status, filter_data_result_with_operator


class ActivityService:

    def __init__(self, activity=Activity()):
        self.activity = activity

    def create(self):
        if self.activity.user_id is not None:
            user_service = UserService.get_one(
                _id=self.activity.user_id)

            if user_service.user is None:
                raise AppLogException(
                    Status.user_not_exists())

            if user_service.user.status == User.STATUSES.inactive:
                raise AppLogException(
                    Status.user_not_exists())
        else:
            raise AppLogException(Status.activity_not_exists())


        self.activity.add()
        self.activity.commit_or_rollback()

        return Status.successfully_processed()


    @classmethod
    def get_one(cls, _id):
        return cls(activity=Activity.query.get_one(_id=_id))


    def alter(self):
        data = ActivityService.get_one(_id=self.activity.id)

        if data.activity is None:
            raise AppLogException(
                Status.activity_not_exists())

        if data.activity.status == Activity.STATUSES.inactive:
            raise AppLogException(
                Status.activity_not_exists())

        if self.activity.user_id is not None:
            if self.activity.user_id != data.activity.user_id:
                user_service = UserService.get_one(
                    _id=self.activity.user_id)

                if user_service.user is None:
                    raise AppLogException(
                        Status.user_not_exists())

                if user_service.user.status == User.STATUSES.inactive:
                    raise AppLogException(
                        Status.user_not_exists())
        else:
            raise AppLogException(Status.please_select_user())


        data.activity.user_id = self.activity.user_id
        data.activity.duration = self.activity.duration
        data.activity.path = self.activity.path

        data.activity.update()
        data.activity.commit_or_rollback()

        self.activity = data.activity

        return Status.successfully_processed()


    @staticmethod
    def get_all_activities(filter_data, paginate_data):
        filter_main = and_()
        if filter_data is not None:
            filter_main = and_(
                filter_main,
                filter_data_result_with_operator(
                    'path', Activity.path,
                    filter_data),
                Activity.user_id == filter_data.get('user_id', None)
                if filter_data.get('user_id', None) is not None else True
                )
        start = paginate_data.get('start') + 1 \
            if paginate_data is not None and paginate_data['start'] else 1

        length = paginate_data.get('length') \
            if paginate_data is not None and paginate_data['length'] else 10

        data = Activity.query.get_all_activities(
            filter_data=filter_main, start = start, length = length
        )

        return data.items, data.total, Status.successfully_processed()


