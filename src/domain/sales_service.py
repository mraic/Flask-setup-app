from sqlalchemy import and_

from src import Property, AppLogException, User, Sale
from src.domain import PropertyService
from src.general import Status, filter_data_result_with_operator



class SaleService:

    def __init__(self, sale = Sale()):
        self.sale = sale

    def create(self):

        if Sale.property_id is not None:
            data = PropertyService.get_one(self.sale.property_id)
            if data.property is not None:
                if data.property.status == Property.STATUSES.inactive:
                    raise AppLogException(Status.property_sold())
                else:
                    data.property.status = Property.STATUSES.inactive

            if self.sale.buyer_id == data.property.owner_id:
                raise AppLogException(Status.user_is_owner())

        if User.status == User.STATUSES.inactive:
            raise AppLogException(Status.user_not_activated())


        self.sale.add()
        self.sale.commit_or_rollback()

        return Status.successfully_processed()

    def alter(self):

        data = SaleService.get_one(Sale.id)
        property_data = PropertyService.get_one(self.sale.property_id)

        if data.sale is None:
            raise AppLogException(Status.sale_doesnt_exists())
        else:
            if property_data.property.status == Property.STATUSES.active:
                property_data.property.status = Property.STATUSES.inactive
                data.sale.properties.status = Property.STATUSES.active
            else:
                property_data.property.status = Property.STATUSES.active
                data.sale.properties.status = Property.STATUSES.inactive


        if User.status == User.STATUSES.inactive:
            raise AppLogException(Status.user_not_activated())

        data.sale.buyer_id = self.sale.buyer_id
        data.sale.property_id = self.sale.property_id

        data.sale.update()
        data.sale.commit_or_rollback()

        self.sale = data.sale

        return Status.successfully_processed()

    def delete(self, _id):

        data = SaleService.get_one(_id = self.sale.id)

        if data.sale is None:
            raise AppLogException(
                Status.sale_doesnt_exists()
            )

        data.sale.delete()
        data.sale.commit_or_rollback()

        return Status.successfully_processed()


    @classmethod
    def get_one(cls, _id):
        return cls(sale=Sale.query.get_one(_id=_id))

    @staticmethod
    def get_all_sales(filter_data, paginate_data):
        filter_main = and_()
        if filter_data is not None:
            filter_main = and_(
                filter_main,
                filter_data_result_with_operator(
                    'first_name', User.first_name,
                    filter_data),
                filter_data_result_with_operator(
                    'last_name', User.last_name,
                    filter_data),
                filter_data_result_with_operator(
                    'email', User.email,
                    filter_data),
                filter_data_result_with_operator(
                    'username', User.username,
                    filter_data)
            )

        start = paginate_data.get('start') +1 \
            if paginate_data is not None and paginate_data['start'] else 1

        length = paginate_data.get('length') \
            if paginate_data is not None and paginate_data['length'] else 10

        data = Sale.query.get_all_sales(
            filter_data = filter_main, start = start, length = length)

        return data.items, data.total, Status.successfully_processed()