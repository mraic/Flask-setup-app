import copy
from types import SimpleNamespace

import pytest


from src import Property, AppLogException, User
from src.domain import PropertyService, SaleService
from src.general import Status


@pytest.mark.usefixtures('dummy_user')
@pytest.mark.usefixtures('dummy_property')
@pytest.mark.usefixtures('dummy_sale')
class TestSaleController:

    def test_create_sale(self, db, mocker):

        mock_property_get_one = mocker.patch(
            "src.domain.sales_service.PropertyService."
            "get_one", autospec = True
        )

        mock_property_get_one.return_value =\
            PropertyService(property=self.dummy_property)

        sale_domain = SaleService(sale=self.dummy_sale)

        sale_status = sale_domain.create()

        assert sale_status.message == Status.successfully_processed().message

    def test_create_sale_property_sold(self, db, mocker):

        mock_property_get_one = mocker.patch(
            "src.domain.sales_service.PropertyService."
            "get_one" , autospec = True
        )

        data = copy.deepcopy(self.dummy_property)
        data.status = Property.STATUSES.inactive

        mock_property_get_one.return_value = PropertyService(property=data)

        sale_domain = SaleService(sale=self.dummy_sale)

        with pytest.raises(AppLogException) as ape:
            sale_domain.create()

        assert ape.value.status.message == Status.property_sold().message

    def test_sale_create_user_id_owner(self, db, mocker):

        mock_property_get_one = mocker.patch(
            "src.domain.sales_service.PropertyService."
            "get_one", autospec = True
        )

        data_property = copy.deepcopy(self.dummy_property)
        data_property.status = Property.STATUSES.active

        mock_property_get_one.return_value = \
            PropertyService(property=data_property)

        data_sale = copy.deepcopy(self.dummy_sale)
        data_sale.buyer_id = self.dummy_property.owner_id

        sale_domain = SaleService(sale=data_sale)

        with pytest.raises(AppLogException) as ape:
            sale_domain.create()

        assert ape.value.status.message == Status.user_is_owner().message


    def test_create_sale_user_not_activated(self, db, mocker):

        mock_property_get_one = mocker.patch(
            "src.domain.sales_service.PropertyService."
            "get_one", autospec=True
        )

        data_property = copy.deepcopy(self.dummy_property)
        data_property.status = Property.STATUSES.active

        mock_property_get_one.return_value =\
            PropertyService(property=data_property)

        sales_domain = SaleService(sale=self.dummy_sale)

        User.status = User.STATUSES.inactive

        with pytest.raises(AppLogException) as ape:
            sales_domain.create()

        assert ape.value.status.message == Status.user_not_activated().message


    def test_alter_sale_get_one(self, db, mocker):

        mock_property_get_one = mocker.patch(
            "src.domain.sales_service.PropertyService."
            "get_one", autospec = True
        )

        mock_property_get_one.return_value =\
            PropertyService(property=self.dummy_property)

        mock_sale_get_one = mocker.patch(
            "src.domain.sales_service.SaleService."
            "get_one", autospec=True
        )

        data = copy.deepcopy(self.dummy_sale)
        data.properties = self.dummy_property
        data.properties.status = Property.STATUSES.active
        mock_sale_get_one.return_value = SaleService(sale=data)

        User.status = User.STATUSES.active


        sale_domain = SaleService(sale=self.dummy_sale)

        sale_status = sale_domain.alter()

        assert sale_status.message == Status.successfully_processed().message

    def test_alter_sale_doesnt_exists(self, db, mocker):

        mock_sale_get_one = mocker.patch(
            "src.domain.sales_service.SaleService."
            "get_one", autospec = True
        )
        mock_sale_get_one.return_value = SaleService(sale=None)

        mock_property_get_one = mocker.patch(
            "src.domain.sales_service.PropertyService."
            "get_one", autospec = True
        )

        mock_property_get_one.return_value = \
            PropertyService(property=self.dummy_property)

        sale_domain = SaleService(sale=self.dummy_sale)

        with pytest.raises(AppLogException) as ape:
            sale_domain.alter()

        assert ape.value.status.message == Status.sale_doesnt_exists().message


    def test_sale_delete(self, db, mocker):

        mock_sale_get_one = mocker.patch(
            "src.domain.sales_service.SaleService."
            "get_one", autospec = True
        )

        mock_sale_get_one.return_value=SaleService(sale=self.dummy_sale)

        sale_domain = SaleService(sale=self.dummy_sale)

        sale_status = sale_domain.delete(_id = self.dummy_sale.id)

        assert sale_status.message == Status.successfully_processed().message

    def test_del_sale_not_exists(self, db, mocker):

        mock_sale_get_one = mocker.patch(
            "src.domain.sales_service.SaleService."
            "get_one", autospec = True
        )

        mock_sale_get_one.return_value = SaleService(sale=None)

        sale_domain = SaleService(sale=self.dummy_sale)

        with pytest.raises(AppLogException) as ape:
            sale_domain.delete(_id = self.dummy_sale.id)

        assert ape.value.status.message == Status.sale_doesnt_exists().message


    def test_get_all_sales(self, db, mocker):

        mock_sale_get_all_sales = mocker.patch(
            "src.domain.sales_service.SaleService."
            "get_all_sales", autospec = True
        )

        total = 1
        data = [SimpleNamespace(Sale=self.dummy_sale)]

        mock_sale_get_all_sales.return_value = \
            SimpleNamespace(items = data, total = total)

        paginate_data = dict(length = 0, start = 0)
        filter_data = {
            "email": {
                "operator": "CONTAINS",
                "value": ""
            },
            "first_name": {
                "operator": "CONTAINS",
                "value": ""
            },
            "last_name": {
                "operator": "CONTAINS",
                "value": ""
            },
            "username": {
                "operator": "CONTAINS",
                "value": ""
            }
        }

        items, total, status = PropertyService.get_all_properties(
            filter_data=filter_data, paginate_data=paginate_data
        )

        assert status.message == Status.successfully_processed().message
        assert total == total
        assert len(data) > 0