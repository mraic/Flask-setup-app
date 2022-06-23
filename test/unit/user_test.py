import copy
from types import SimpleNamespace

import pytest
from faker import Faker


from src import AppLogException, User
from src.domain import UserService
from src.general import Status


@pytest.mark.usefixtures("dummy_user")
class TestUserController:

    def test_create_user(self, db, mocker):
        mock_user_get_one_by_username = mocker.patch(
            "src.domain.user_service.UserService."
            "check_if_already_exists_by_username", autospec=True)

        mock_user_get_one_by_username.return_value = None

        mock_user_get_one_by_email = mocker.patch(
            "src.domain.user_service.UserService."
            "check_if_already_exists_by_email", autospec=True)

        mock_user_get_one_by_email.return_value = None

        user_domain = UserService(user=self.dummy_user)

        status_create = user_domain.create()

        assert status_create.message == Status.successfully_processed().message

    def test_create_user_already_exist_by_username(self, db, mocker):
        mock_user_get_one_by_username = mocker.patch(
            "src.domain.user_service.UserService."
            "check_if_already_exists_by_username", autospec=True)

        mock_user_get_one_by_username.return_value = self.dummy_user

        user_domain = UserService(user=self.dummy_user)
        with pytest.raises(AppLogException) as ape:
            user_domain.create()

        assert Status.user_already_exists().message == \
               ape.value.status.message

    def test_create_user_already_exist_by_email(self, db, mocker):
        mock_user_get_one_by_username = mocker.patch(
            "src.domain.user_service.UserService."
            "check_if_already_exists_by_username", autospec=True)

        mock_user_get_one_by_username.return_value = None

        mock_user_get_one_by_email = mocker.patch(
            "src.domain.user_service.UserService."
            "check_if_already_exists_by_email", autospec=True)

        mock_user_get_one_by_email.return_value = self.dummy_user

        user_domain = UserService(user=self.dummy_user)
        with pytest.raises(AppLogException) as ape:
            user_domain.create()

        assert Status.email_already_exists().message == \
               ape.value.status.message


    def test_alter_user(self, db, mocker):
        mock_user_get_one = mocker.patch(
            "src.domain.user_service.UserService.get_one", autospec = True
        )

        mock_user_get_one.return_value = UserService(user=self.dummy_user)

        mock_user_already_exists_ex_this = mocker.patch(
            "src.domain.user_service.UserService."
            "check_if_username_already_exists_exclude_this", autospec=True
        )
        mock_user_already_exists_ex_this.return_value = None

        mock_user_email_exists_exclude_this = mocker.patch(
            "src.domain.user_service.UserService."
            "check_if_email_already_exists_exclude_this", autospec=True
        )
        mock_user_email_exists_exclude_this.return_value = None

        user_domain = UserService(user=self.dummy_user)

        status_alter = user_domain.alter()

        assert status_alter.message == Status.successfully_processed().message

    def test_alter_user_not_exist(self, db, mocker):
        mock_user_get_one = mocker.patch(
            "src.domain.user_service.UserService.get_one", autospec = True
        )
        mock_user_get_one.return_value = UserService(user=None)

        user_domain = UserService(user=self.dummy_user)
        with pytest.raises(AppLogException) as ape:
            user_domain.alter()

        assert Status.user_not_exists().message == \
               ape.value.status.message

    def test_alter_check_if_username_already_exists(self, db, mocker):
        mock_user_get_one = mocker.patch(
            "src.domain.user_service.UserService.get_one", autospec=True
        )

        mock_user_get_one.return_value = UserService(user=self.dummy_user)


        mock_user_check_if_username_already_exists = mocker.patch(
            "src.domain.user_service.UserService."
            "check_if_username_already_exists_exclude_this", autospec=True
        )

        mock_user_check_if_username_already_exists.return_value =\
            self.dummy_user

        user_domain = UserService(user=self.dummy_user)
        with pytest.raises(AppLogException) as ape:
            user_domain.alter()

        assert Status.username_already_taken().message\
               == ape.value.status.message

    def test_alter_check_if_email_already_exists(self, db, mocker):
        mock_user_get_one = mocker.patch(
            "src.domain.user_service.UserService.get_one",autospec=True
        )

        mock_user_get_one.return_value = UserService(user=self.dummy_user)

        mock_user_check_if_username_already_exists = mocker.patch(
            "src.domain.user_service.UserService."
            "check_if_username_already_exists_exclude_this", autospec=True
        )

        mock_user_check_if_username_already_exists.return_value = None

        mock_user_check_if_email_already_exists_exclude_this = mocker.patch(
            "src.domain.user_service.UserService."
            "check_if_email_already_exists_exclude_this", autospec=True
        )

        mock_user_check_if_email_already_exists_exclude_this.return_value =\
            self.dummy_user

        user_domain = UserService(user = self.dummy_user)

        with pytest.raises(AppLogException) as ape:
            user_domain.alter()

        assert Status.username_already_taken().message == \
               ape.value.status.message

    def test_deactivate_user(self, db, mocker):

        mock_user_get_one = mocker.patch(
            "src.domain.user_service.UserService.get_one", autospec = True
        )

        mock_user_get_one.return_value = UserService(user=self.dummy_user)

        user_domain = UserService(user=self.dummy_user)

        status_deactivate = user_domain.deactivate(None)

        assert status_deactivate.message ==\
        Status.successfully_processed().message

    def test_deactivate_self_deactivate(self, db, mocker):
        fake = Faker()
        mock_user_get_one = mocker.patch(
            "src.domain.user_service.UserService.get_one", autospec=True
        )

        self.dummy_user.id = fake.uuid4()
        mock_user_get_one.return_value = UserService(user=self.dummy_user)

        user_domain = UserService(user=self.dummy_user)

        with pytest.raises(AppLogException) as ape:
            user_domain.deactivate(self.dummy_user.id)

        assert Status.can_not_self_deactivate().message == \
               ape.value.status.message


    def test_check_if_user_exists_deactivate(self, db, mocker):

        fake = Faker()
        mock_user_get_one = mocker.patch(
            "src.domain.user_service.UserService.get_one", autospec=True
        )

        data = copy.deepcopy(self.dummy_user)
        data.id = fake.uuid4()


        mock_user_get_one.return_value = UserService(user=None)

        user_domain = UserService(user=data)

        with pytest.raises(AppLogException) as ape:
            user_domain.deactivate(data.id)

        assert ape.value.status.message ==\
               Status.user_not_exists().message


    def test_activate_user(self, db, mocker):

        mock_user_get_one = mocker.patch(
            "src.domain.user_service.UserService.get_one", autospec = True
        )

        data = copy.deepcopy(self.dummy_user)
        data.status = User.STATUSES.inactive

        mock_user_get_one.return_value = UserService(user=data)

        user_domain = UserService(user=data)

        status_activate  = user_domain.activate()

        assert status_activate.message == \
               Status.successfully_processed().message

    def test_activate_user_not_exists(self, db, mocker):

        mock_user_get_one = mocker.patch(
            "src.domain.user_service.UserService.get_one", autospec=True
        )

        mock_user_get_one.return_value = UserService(user=None)

        user_domain = UserService(user = self.dummy_user)

        with pytest.raises(AppLogException) as ape:
            user_domain.activate()

        assert ape.value.status.message == Status.user_not_exists().message


    def test_activate_activated_user(self, db, mocker):

        mock_user_get_one = mocker.patch(
            "src.domain.user_service.UserService.get_one", autospec = True
        )
        data = copy.deepcopy(self.dummy_user)
        data.status = User.STATUSES.active

        mock_user_get_one.return_value = UserService(user=data)

        user_domain = UserService(user=data)

        with pytest.raises(AppLogException) as ape:
            user_domain.activate()

        assert ape.value.status.message == \
               Status.user_already_activated().message


    def test_login_user(self, db, mocker):
        fake = Faker()

        mock_user_get_one_by_username = mocker.patch(
            "src.domain.user_service.UserService."
            "get_one_by_username", autospec=True
        )

        mock_user_get_one_by_username.return_value = \
            UserService(user=self.dummy_user)

        mock_check_password = mocker.patch(
            "src.domain.user_service.UserService."
            "get_access_token", autospec=True
        )
        mock_check_password.return_value = None, \
                                           Status.successfully_processed()

        mock_check_password_hash = mocker.patch(
            "src.domain.user_service."
            "check_password_hash", autospec = True
        )

        mock_check_password_hash.return_value = True



        self.dummy_user.id = fake.uuid4()
        self.dummy_user.status = User.STATUSES.active
        user_domain = UserService(user=self.dummy_user)

        status_login, data = user_domain.login()

        assert status_login.message == Status.successfully_processed().message

    def test_login_user_none(self, db, mocker):

        mock_user_get_one_by_username = mocker.patch(
            "src.domain.user_service.UserService."
            "get_one_by_username", autospec = True
        )

        mock_user_get_one_by_username.return_value = \
            UserService(user=None)

        user_domain = UserService(user=self.dummy_user)

        with pytest.raises(AppLogException) as ape:
            user_domain.login()

        assert Status.login_failed().message == ape.value.status.message

    def test_login_user_status(self, db, mocker):

        mock_user_get_one_by_username = mocker.patch(
            "src.domain.user_service.UserService."
            "get_one_by_username", autospec=True
        )

        data = copy.deepcopy(self.dummy_user)
        data.status = User.STATUSES.inactive

        mock_user_get_one_by_username.return_value = UserService(user=data)

        user_domain = UserService(user=data)

        with pytest.raises(AppLogException) as ape:
            user_domain.login()

        assert Status.user_not_activated().message ==\
            ape.value.status.message


    def test_pagination(self, db, mocker):
        mock_users = mocker.patch(
            "src.models.users.UserQuery."
            "get_all_users", autospec=True
        )
        total = 1
        data = [SimpleNamespace(User=self.dummy_user,  total_=total)]

        mock_users.return_value = SimpleNamespace(
            items = data, total=total
        )
        paginate_date = dict(length=0, start=0)
        filter_date = {
            "email": {
                "operator": "CONTAINS",
                "value": ""
            },
            "first_name":{
                "operator": "CONTAINS",
                "value": ""
            },
            "last_name":{
                "operator": "CONTAINS",
                "value": ""
            },
            "username":{
                "operator": "CONTAINS",
                "value": ""
            }
        }

        data, total, status = UserService.get_all_users(
            filter_data=filter_date, paginate_data=paginate_date)

        assert status.message == Status.successfully_processed().message
        assert total == total
        assert len(data) > 0