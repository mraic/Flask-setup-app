import enum
from uuid import uuid4
from sqlalchemy import orm, or_, func

from .common import BaseModelMixin, ModelsMixin
from .. import db
from ..models.common import BaseQueryMixin
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

class UserQuery(BaseQueryMixin, db.Query):

    def get_one(self, _id):
        try:
            return self.filter(User.id == _id).first()
        except Exception as e:
            db.session.rollback()
            raise e

    def check_if_already_exists_by_username(self, username):
        try:
            return self.filter(User.username == username).first() is not None
        except Exception as e:
            db.session.rollback()
            raise e

    def check_if_already_exists_by_email(self,email):
        try:
            return self.filter(User.email == email).first() is not None
        except Exception as e:
            db.session.rollback()
            raise e

    def get_one_by_username(self, username):
        try:
            return self.filter(
                User.username == username,
                User.status == User.STATUSES.active
            ).first()
        except Exception as e:
            db.session.rollback()
            raise e

    def get_one_by_email(self, email):
        try:
            return self.filter(
                User.email == email,
                User.status == User.STATUSES.active
            ).first()
        except Exception as e:
            raise e

    @staticmethod
    def get_all_users(filter_data, start, length):
        try:
            from src import Activity

            subquery = db.session.query(
                Activity.user_id,
                func.count(Activity.id).label('total_')
            ).filter(
                Activity.status == Activity.STATUSES.active
            ).group_by(
                Activity.user_id
            ).subquery()

            return db.session.query(
                User, subquery
            ).join(
                subquery,
                User.id == subquery.c.user_id,
                isouter=True
            ).filter(
                filter_data,
                User.status == User.STATUSES.active
            ).order_by(
                User.created_at.desc()
            ).paginate(
                page=start, per_page=length, error_out=False, max_per_page=50)
        except Exception as e:
            db.session.rollback()
            raise e


    def check_if_username_already_exists_exclude_this(self, _id, username):
        try:
            return self.filter(
                User.username == username,
                User.id != _id
            ).first() is not None

        except Exception as e:
            db.session.rollback()
            raise e

    def check_if_email_already_exists_exclude_this(self, _id, email):
        try:
            return self.filter(
                User.email == email,
                User.id != _id
            ).first() is not None

        except Exception as e:
            db.session.rollback()
            raise e

    def autocomplete(self, search):
        try:
            return self.filter(
                User.status == User.STATUSES.active,
                or_(
                    User.first_name.ilike('%'+ search + '%'),
                    User.last_name.ilike('%' + search + '%')
                )
                ).all()
            pass
        except Exception as e:
            db.session.rollback()
            raise e

class UserStatus(enum.Enum):
    inactive = 0
    active = 1


class User(BaseModelMixin, ModelsMixin, db.Model):
    __tablename__ = "users"
    query_class = UserQuery

    STATUSES = UserStatus


    id = sa.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    username = sa.Column(sa.String(255), nullable = True, unique = True)
    first_name = sa.Column(sa.String(255), nullable = False, index=True)
    last_name = sa.Column(sa.String(255), nullable=False)
    email = sa.Column(sa.String(255), nullable = False, unique = True)
    password = sa.Column(sa.String(255), nullable = False)
    status = sa.Column(
        sa.Enum(
            UserStatus,
            name="ck_users_statuses",
            native_enum=False,
            create_constraint=True,
            length=255,
            validate_strings=True,
        ),
        nullable=False,
        default=UserStatus.inactive,
        server_default=UserStatus.inactive.name)

    activities = orm.relationship("Activity", back_populates="user")
    properties = orm.relationship("Property", back_populates ="owner")
    sale = orm.relationship("Sale", back_populates="user")






