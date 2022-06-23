import enum
from datetime import timedelta

from sqlalchemy import orm

from .common import BaseModelMixin, ModelsMixin
from uuid import uuid4
from .. import db
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa

class ActivityQuery(BaseModelMixin, db.Query):

    def get_one(self, _id):
        try:
            return self.filter(Activity.id == _id).first()
        except Exception as e:
            db.session.rollback()
            raise e

    def get_all_activities(self, filter_data, start, length):
        try:
            return self.filter(
                filter_data,
                Activity.duration < timedelta(milliseconds=0.1)
            ).paginate(
                page = start,
                per_page = length, error_out = False, max_per_page=50)
        except Exception as e:
            db.session.rollback()
            raise e


class ActivityStatus(enum.Enum):
    inactive = 0
    active = 1

class Activity(BaseModelMixin, ModelsMixin, db.Model):

    __tablename__ = "activities"
    query_class = ActivityQuery

    STATUSES = ActivityStatus


    id = sa.Column(UUID(as_uuid=True), default = uuid4, primary_key = True)
    duration = sa.Column(sa.Time(), nullable = False)
    path = sa.Column(sa.String(255), nullable = False)
    status = sa.Column(
        sa.Enum(
            ActivityStatus,
            name="ck_activities_statuses",
            native_enum=False,
            create_constraint=True,
            length=255,
            validate_strings=True,
        ),
        nullable=False,
        default=ActivityStatus.active,
        server_default=ActivityStatus.active.name)

    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('users.id', ondelete="RESTRICT"),
                        nullable=False,
                        index=True)

    user = orm.relationship("User", back_populates="activities", uselist=False)

