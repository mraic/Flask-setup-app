import copy
from types import SimpleNamespace

import pytest
from faker import Faker

from src import AppLogException, User, Activity
from src.domain import ActivityService, UserService
from src.general import Status


@pytest.mark.usefixtures("dummy_activity")
@pytest.mark.usefixtures("dummy_user")
class TestActivityController:

    def test_create_activity(self, db, mocker):

        mock_user_user_id = mocker.patch(
            "src.domain.activity_service.ActivityService", autospec=True
        )

        mock_user_user_id.return_value = \
            ActivityService(activity=self.dummy_activity)

        mock_user_get_one = mocker.patch(
            "src.domain.activity_service.UserService."
            "get_one", autospec = True
        )

        mock_user_get_one.return_value = UserService(user=self.dummy_user)


        activity_domain = ActivityService(activity=self.dummy_activity)

        status_create = activity_domain.create()

        assert status_create.message == \
               Status.successfully_processed().message

    def test_create_activity_not_exists(self, db, mocker):

        test_create_activity_not_exists = mocker.patch(
            "src.domain.activity_service.ActivityService", autospec=True
        )

        data = copy.deepcopy(self.dummy_activity)
        data.user_id = None

        test_create_activity_not_exists.return_value = \
            ActivityService(activity=data)

        activity_domain = ActivityService(activity=data)

        with pytest.raises(AppLogException) as ape:
            activity_domain.create()

        assert ape.value.status.message == Status.activity_not_exists().message


    def test_create_activity_user_not_exists(self, db, mocker):

        mock_user_not_exists = mocker.patch(
            "src.domain.activity_service.UserService."
            "get_one"
        )

        mock_user_not_exists.return_value = UserService(user=None)

        activity_domain = ActivityService(activity=self.dummy_activity)

        with pytest.raises(AppLogException) as ape:
            activity_domain.create()

        assert ape.value.status.message == Status.user_not_exists().message


    def test_create_activity_user_no_status(self, db, mocker):

        mock_user_not_exists = mocker.patch(
            "src.domain.activity_service.UserService."
            "get_one", autospec =True
            )

        data = copy.deepcopy(self.dummy_user)
        data.status = User.STATUSES.inactive

        mock_user_not_exists.return_value = UserService(user=data)

        activity_domain = ActivityService(activity=self.dummy_activity)

        with pytest.raises(AppLogException) as ape:
            activity_domain.create()

        assert ape.value.status.message == Status.user_not_exists().message

    def test_alter_activity_service(self, db, mocker):

        mock_activity_get_one = mocker.patch(
            "src.domain.activity_service.ActivityService."
            "get_one",autospec=True
        )

        mock_activity_get_one.return_value = \
            ActivityService(activity=self.dummy_activity)

        mock_user_get_one = mocker.patch(
            "src.domain.activity_service.UserService."
            "get_one",autospec=True
        )

        mock_user_get_one.return_value = UserService(user=self.dummy_user)

        activity_domain = ActivityService(activity=self.dummy_activity)

        activity_status = activity_domain.alter()

        assert activity_status.message == \
               Status.successfully_processed().message


    def test_activity_is_none(self, db, mocker):

        mock_activity_get_one = mocker.patch(
            "src.domain.activity_service.ActivityService."
            "get_one", autospec=True
        )

        mock_activity_get_one.return_value = ActivityService(activity=None)

        activity_domain = ActivityService(activity=self.dummy_activity)

        with pytest.raises(AppLogException) as ape:
            activity_domain.alter()

        assert ape.value.status.message == Status.activity_not_exists().message

    def test_activity_status_is_none(self, db, mocker):

        mock_activity_get_one = mocker.patch(
            "src.domain.activity_service.ActivityService."
            "get_one"
        )

        data = copy.deepcopy(self.dummy_activity)
        data.status = Activity.STATUSES.inactive

        mock_activity_get_one.return_value = ActivityService(activity=data)

        activity_domain = ActivityService(activity=data)

        with pytest.raises(AppLogException) as ape:
            activity_domain.alter()

        assert ape.value.status.message == Status.activity_not_exists().message


    def test_activity_user_not_exists(self, db, mocker):

        fake = Faker()

        mock_activity_get_one= mocker.patch(
            "src.domain.activity_service.ActivityService."
            "get_one", autospec =True
        )

        data = copy.deepcopy(self.dummy_activity)
        data.user_id = fake.uuid4()

        mock_activity_get_one.return_value = \
            ActivityService(activity=data)

        mock_user_get_one = mocker.patch(
            "src.domain.activity_service.UserService."
            "get_one"
        )

        mock_user_get_one.return_value = UserService(user=None)

        activity_domain = ActivityService(activity=self.dummy_activity)

        with pytest.raises(AppLogException) as ape:
            activity_domain.alter()

        assert ape.value.status.message == Status.user_not_exists().message


    def test_activity_user_not_exists__(self, db, mocker):

        fake = Faker()

        mock_activity_get_one = mocker.patch(
            "src.domain.activity_service.ActivityService."
            "get_one", autospec=True
        )

        data = copy.deepcopy(self.dummy_activity)
        data.user_id = fake.uuid4()

        mock_activity_get_one.return_value = ActivityService(activity=data)

        mock_user_get_one = mocker.patch(
            "src.domain.activity_service.UserService."
            "get_one", autospec=True
        )

        user_data = self.dummy_user
        user_data.status = User.STATUSES.inactive

        mock_user_get_one.return_value = UserService(user=self.dummy_user)

        activity_domain = ActivityService(activity=self.dummy_activity)

        with pytest.raises(AppLogException) as ape:
            activity_domain.alter()

        assert ape.value.status.message == Status.user_not_exists().message


    def test_pagination(self, db, mocker):
        mock_users = mocker.patch(
            "src.models.activities.ActivityQuery."
            "get_all_activities", autospec=True
        )
        total = 1
        data = [SimpleNamespace(User=self.dummy_activity)]
        mock_users.return_value = SimpleNamespace(
            items = data, total=total
        )
        paginate_date = dict(length=0, start=0)
        filter_date = {
            "path": {
              "operator": "CONTAINS",
              "value": ""
    },
            "user_id": ""
        }

        data, total, status = ActivityService.get_all_activities(
            filter_data=filter_date, paginate_data=paginate_date)

        assert status.message == Status.successfully_processed().message
        assert total == total
        assert len(data) > 0

