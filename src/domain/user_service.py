from datetime import datetime, timezone, timedelta

import jwt
from flask import current_app
from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash

from .. import User, AppLogException
from ..general import Status, filter_data_result_with_operator
from ..views import UserSchema


class UserService:

    def __init__(self, user=User()):
        self.user = user

    def create(self):
        if UserService.check_if_already_exists_by_username(
                username=self.user.username):
            raise AppLogException(Status.user_already_exists())

        if UserService.check_if_already_exists_by_email(
            email = self.user.email):
            raise AppLogException(Status.email_already_exists())

        self.user.password = generate_password_hash(self.user.password)
        self.user.add()
        self.user.commit_or_rollback()
        return Status.successfully_processed()

    def alter(self):
        data = UserService.get_one(_id=self.user.id)

        if data.user is None:
            raise AppLogException(Status.user_not_exists())

        if data.user.status == User.STATUSES.inactive:
            raise AppLogException(Status.user_not_exists())

        if UserService.check_if_username_already_exists_exclude_this(
            _id=data.user.id,  username=self.user.username):
            raise AppLogException(Status.username_already_taken())

        if UserService.check_if_email_already_exists_exclude_this(
                _id=data.user.id, email=self.user.email):
            raise AppLogException(Status.username_already_taken())

        data.user.first_name = self.user.first_name
        data.user.last_name = self.user.last_name
        data.user.email = self.user.email
        data.user.username = self.user.username

        data.user.update()
        data.user.commit_or_rollback()

        self.user = data.user

        return Status.successfully_processed()

    @classmethod
    def get_one(cls, _id):
        return cls(user=User.query.get_one(_id=_id))

    def deactivate(self, current_user_id):
        data = UserService.get_one(_id=self.user.id)

        if data.user is None:
            raise AppLogException(
                Status.user_not_exists())

        if str(data.user.id) == current_user_id:
            raise AppLogException(Status.can_not_self_deactivate())


        data.user.status = User.STATUSES.inactive

        data.user.update()
        data.user.commit_or_rollback()

        self.user = data.user

        return Status.successfully_processed()

    def activate(self):
        data = UserService.get_one(_id = self.user.id)

        if data.user is None:
            raise AppLogException(Status.user_not_exists())

        if data.user.status == data.user.STATUSES.active:
            raise AppLogException(Status.user_already_activated())

        data.user.status = User.STATUSES.active

        data.user.update()
        data.user.commit_or_rollback()

        self.user = data.user

        return Status.successfully_processed()

    def reset_password(self, new_password):
        data = UserService.get_one(_id = self.user.id)

        if data.user is None:
            raise AppLogException(Status.user_not_exists())

        if data.user.status == User.STATUSES.inactive:
            raise AppLogException(Status.user_not_exists())

        if not check_password_hash(data.user.password, self.user.password):
            raise AppLogException(Status.password_is_incorrect())

        data.user.password = generate_password_hash(new_password)

        data.user.update()
        data.user.commit_or_rollback()

        self.user = data.user

        return Status.successfully_processed()

    def reset_password_by_id(self, _id, new_password, confirm_new_password):

        data = UserService.get_one(_id = _id)

        if data.user is None:
            raise AppLogException(Status.user_not_exists())

        if data.user.status == User.STATUSES.inactive:
            raise AppLogException(Status.user_not_exists())

        if not check_password_hash(data.user.password, self.user.password):
            raise AppLogException(Status.password_is_incorrect())

        if new_password == confirm_new_password:

            data.user.password = generate_password_hash(new_password)

            data.user.update()
            data.user.commit_or_rollback()

            self.user = data.user

            return Status.successfully_processed()


    def login(self):
        data = UserService.get_one_by_username(username=self.user.username)

        if data.user is None:
            raise AppLogException(Status.login_failed())

        if data.user.status == User.STATUSES.inactive:
            raise AppLogException(Status.user_not_activated())

        if not check_password_hash(data.user.password, self.user.password):
            raise AppLogException(Status.login_failed())

        access_token, _ = UserService.get_access_token(data.user.id)
        schema = UserSchema()
        data_dict = schema.dump(data.user)
        data_dict['access_token'] = access_token

        self.user = data.user

        return Status.successfully_processed(), data_dict


    @staticmethod
    def login_user(username, password):

        data = UserService.get_one_by_username(username=username)

        if data.user is None:
            raise AppLogException(Status.login_failed())

        if data.user.status == User.STATUSES.inactive:
            raise AppLogException(Status.user_not_activated())

        if not check_password_hash(data.user.password, password):
            raise AppLogException(Status.login_failed())

        access_token, _ = UserService.get_access_token(data.user.id)
        schema = UserSchema()
        data_dict = schema.dump(data.user)
        data_dict['access_token'] = access_token


        return data_dict, Status.successfully_processed()

    @classmethod
    def get_one_by_username(cls, username):
        return cls(user=User.query.get_one_by_username(username=username))

    @classmethod
    def get_one_by_email(cls, email):
        return cls(user=User.query.get_one_by_email(email=email))

    @staticmethod
    def check_if_already_exists_by_username(username):
        return User.query.check_if_already_exists_by_username(
            username=username)

    @staticmethod
    def check_if_already_exists_by_email(email):
        return User.query.check_if_already_exists_by_email(
            email = email)

    @staticmethod
    def get_all_users(filter_data, paginate_data):
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
                    filter_data))

        start = paginate_data.get('start') + 1 \
            if paginate_data is not None and paginate_data['start'] else 1

        length = paginate_data.get('length') \
            if paginate_data is not None and paginate_data['length'] else 10

        data = User.query.get_all_users(
            filter_data=filter_main,start=start, length=length)

        list_data = []
        schema = UserSchema()
        for i in data.items or []:
            current_dict = schema.dump(i.User)
            current_dict['total_'] = i.total_ or 0
            list_data.append(current_dict)

        return list_data, data.total, Status.successfully_processed()

    @staticmethod
    def get_access_token(_id):

        access_token = jwt.encode({
            'id': str(_id),
            'exp': datetime.now(tz=timezone.utc) + timedelta(
                seconds=current_app.config.get('JWT_EXPIRES_IN'))},
            current_app.config.get('JWT_SECRET_KEY'))

        return access_token, Status.successfully_processed()

    @staticmethod
    def check_if_username_already_exists_exclude_this(_id, username):
        return User.query.check_if_username_already_exists_exclude_this(
            _id=_id, username=username)

    @staticmethod
    def check_if_email_already_exists_exclude_this(_id, email):
        return User.query.check_if_email_already_exists_exclude_this(
            _id=_id, email=email)

    @staticmethod
    def autocomplete(search):
        data = User.query.autocomplete(search=search)

        return data, Status.successfully_processed()





