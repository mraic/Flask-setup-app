import copy
from types import SimpleNamespace

import pytest
from faker import Faker

from src import AppLogException, User, Property
from src.domain import UserService, PropertyService
from src.general import Status


@pytest.mark.usefixtures('dummy_property')
@pytest.mark.usefixtures('dummy_user')
class TestPropertyController:

    def test_create_property(self, db, mocker):

        mock_user_get_one = mocker.patch(
            "src.domain.property_service.UserService."
            "get_one", autospec = True
        )

        mock_user_get_one.return_value = UserService(user=self.dummy_user)

        property_domain = PropertyService(property=self.dummy_property)

        property_status = property_domain.create()

        assert property_status.message == \
               Status.successfully_processed().message


    def test_property_user_not_exists(self, db, mocker):

        fake = Faker()

        mock_user_get_one = mocker.patch(
            "src.domain.property_service.UserService."
            "get_one", autospec = True
        )

        mock_user_get_one.return_value = UserService(user=None)

        data = copy.deepcopy(self.dummy_property)
        data.owner_id = fake.uuid4()

        property_domain = PropertyService(property=data)

        with pytest.raises(AppLogException) as ape:
            property_domain.create()

        assert ape.value.status.message == Status.user_not_exists().message

    def test_property_status_inactive(self, db, mocker):

        fake = Faker()

        mock_user_get_one = mocker.patch(
            "src.domain.property_service.UserService."
            "get_one", autospec = True
        )

        data = copy.deepcopy(self.dummy_user)
        data.status = User.STATUSES.inactive

        mock_user_get_one.return_value = UserService(user=data)

        property_domain = PropertyService(property = self.dummy_property)

        with pytest.raises(AppLogException) as ape:
            property_domain.create()

        assert ape.value.status.message == Status.user_not_activated().message

    def test_alter_property(self, db, mocker):


        mock_property_get_one = mocker.patch(
            "src.domain.property_service.PropertyService."
            "get_one", autospec =True
        )

        mock_property_get_one.return_value = \
            PropertyService(property=self.dummy_property)

        mock_user_get_one = mocker.patch(
            "src.domain.property_service.UserService."
            "get_one", autospec=True
        )

        mock_user_get_one.return_value = \
            UserService(user=self.dummy_user)


        property_domain = PropertyService(property=self.dummy_property)

        property_status = property_domain.alter()

        assert property_status.message == \
               Status.successfully_processed().message

    def test_alter_property_doesnot_exists(self, db, mocker):

        mock_property_get_one = mocker.patch(
            "src.domain.property_service.PropertyService."
            "get_one", autospec=True
        )

        mock_property_get_one.return_value = \
            PropertyService(property=None)

        property_domain = PropertyService(property=self.dummy_property)

        with pytest.raises(AppLogException) as ape:
            property_domain.alter()

        assert ape.value.status.message ==\
               Status.property_doesnot_exists().message

    def test_alter_user_not_activated(self, db, mocker):
        mock_property_get_one = mocker.patch(
            "src.domain.property_service.PropertyService."
            "get_one", autospec=True
        )

        mock_property_get_one.return_value = \
            PropertyService(property=self.dummy_property)

        data = copy.deepcopy(self.dummy_user)
        data.status = User.STATUSES.inactive

        mock_user_get_one = mocker.patch(
            "src.domain.property_service.UserService."
            "get_one", autospec=True
        )

        mock_user_get_one.return_value = UserService(user=data)

        property_domain = PropertyService(property=self.dummy_property)

        with pytest.raises(AppLogException) as ape:
            property_domain.alter()

        assert ape.value.status.message == Status.user_not_activated().message


    def test_property_activate(self, db, mocker):
        fake = Faker()

        mock_property_get_one = mocker.patch(
            "src.domain.property_service.PropertyService."
            "get_one", autospec = True
        )

        data = copy.deepcopy(self.dummy_property)
        data.id = fake.uuid4()

        mock_property_get_one.return_value = \
            PropertyService(property=data)

        property_domain = PropertyService(property=self.dummy_property)

        property_status = property_domain.activate(_id=self.dummy_property.id)

        assert property_status.message ==\
               Status.successfully_processed().message

    def test_property_not_exist(self, db, mocker):

        mock_property_get_one = mocker.patch(
            "src.domain.property_service.PropertyService."
            "get_one", autospec = True
        )

        mock_property_get_one.return_value =\
            PropertyService(property=self.dummy_property)

        property_domain = PropertyService(property=self.dummy_property)

        with pytest.raises(AppLogException) as ape:
            property_domain.activate(_id = self.dummy_property.id)

        assert ape.value.status.message == \
               Status.property_doesnot_exists().message

    def test_property_status(self, db, mocker):

        fake = Faker()

        mock_property_get_one = mocker.patch(
            "src.domain.property_service.PropertyService."
            "get_one", autospec = True
        )

        data = copy.deepcopy(self.dummy_property)
        data.status = Property.STATUSES.active
        data.id = fake.uuid4()

        mock_property_get_one.return_value = PropertyService(property=data)

        property_domain = PropertyService(property=self.dummy_property)

        with pytest.raises(AppLogException) as ape:
            property_domain.activate(_id = self.dummy_property.id)

        assert ape.value.status.message == Status.property_active().message


    def test_paginate(self, db, mocker):

        mock_property_get_all_properties = mocker.patch(
            "src.domain.property_service.PropertyService."
            "get_all_properties", autospec = True
        )

        total = 1
        data = [SimpleNamespace(Property=self.dummy_property)]


        mock_property_get_all_properties.return_value = \
            SimpleNamespace(items = data, total = total)

        paginate_data = dict(length = 0, start = 0)
        filter_data = {
            "address": {
                "operator": "CONTAINS",
                "value": ""
            },
            "living_area": {
              "_from": "",
              "_to": ""
            },
            "price": {
              "_from": "",
              "_to": ""
            }
        }

        items, total, status = PropertyService.get_all_properties(
            filter_data=filter_data, paginate_data=paginate_data
        )

        assert status.message == Status.successfully_processed().message
        assert total == total
        assert len(data) > 0




