from sqlalchemy import and_

from src import Property, AppLogException, User
from src.domain import UserService
from src.general import Status, filter_data_result_with_operator, \
    filter_data_result_between_two_values


class PropertyService:

    def __init__(self, property=Property()):
        self.property = property

    def create(self):

        if self.property.owner_id is not None:
            user_service = UserService.get_one(_id=self.property.owner_id)
            if user_service.user is None:
                raise AppLogException(
                    Status.user_not_exists()
                )
            if user_service.user.status == User.STATUSES.inactive:
                raise AppLogException(
                    Status.user_not_activated()
                )

        self.property.add()
        self.property.commit_or_rollback()

        return Status.successfully_processed()


    def alter(self):
        data = PropertyService.get_one(_id=self.property.id)

        if data.property is None:
            raise AppLogException(Status.property_doesnot_exists())

        user_service = UserService.get_one(_id = data.property.owner_id)

        if user_service.user.status == User.STATUSES.inactive:
            raise AppLogException(
                Status.user_not_activated()
                )

        data.property.address = self.property.address
        data.property.price = self.property.price
        data.property.living_area = self.property.living_area
        data.property.owner_id = self.property.owner_id

        data.property.update()
        data.property.commit_or_rollback()

        self.property = data.property

        return Status.successfully_processed()

    def deactivate(self, _id):
        data = PropertyService.get_one(_id = self.property.id)

        if data.property.id is None:
            raise AppLogException(
                Status.property_doesnot_exists()
            )

        if data.property.status is Property.STATUSES.inactive:
            raise AppLogException(
                Status.property_deactivated()
            )

        if data.property.status == Property.STATUSES.active:
            data.property.status = Property.STATUSES.inactive

        data.property.update()
        data.property.commit_or_rollback()

        self.property = data.property

        return Status.successfully_processed()

    def activate(self, _id):
        data = PropertyService.get_one(_id = self.property.id)

        if data.property.id is None:
            raise AppLogException(
                Status.property_doesnot_exists()
            )

        if data.property.status is Property.STATUSES.active:
            raise AppLogException(
                Status.property_active()
            )

        if data.property.status == Property.STATUSES.inactive:
            data.property.status = Property.STATUSES.active

        data.property.update()
        data.property.commit_or_rollback()

        self.property = data.property

        return Status.successfully_processed()

    @classmethod
    def get_one(cls,_id):
        return cls(property=Property.query.get_one(_id=_id))

    @staticmethod
    def get_all_properties(filter_data, paginate_data):
        filter_main = and_()
        if filter_data is not None:
            filter_main = and_(
                filter_main,
                filter_data_result_with_operator(
                    'address', Property.address, filter_data),

                filter_data_result_between_two_values('living_area',
                                                    '_from',
                                                    '_to',
                                                    Property.living_area,
                                                    filter_data),

                filter_data_result_between_two_values('price',
                                                    '_from',
                                                    '_to',
                                                    Property.price,
                                                    filter_data),
            )

        start = paginate_data.get('start') +1 \
            if paginate_data is not None and paginate_data['start'] else 1

        length = paginate_data.get['length'] \
            if paginate_data is not None and paginate_data['length'] else 10

        data = Property.query.get_all_properties(
            filter_data=filter_main, start = start, length=length)

        return  data.items, data.total, Status.successfully_processed()
    
