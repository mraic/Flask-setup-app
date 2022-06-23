from datetime import datetime

import enum
from sqlalchemy import orm, func, text

from .common import BaseModelMixin, ModelsMixin
from uuid import uuid4
from ..import db
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa

class PropertyQuery(BaseModelMixin, db.Query):

    def get_one(self,_id):
        try:
            return self.filter(Property.id==_id).first()
        except Exception as e:
            db.session.rollback()
            raise e


    def get_all_properties(self,filter_data, start, length):
        try:
            return self.filter(
                filter_data,
                Property.status == Property.STATUSES.active
            ).paginate(
                page=start,
                per_page= length, error_out=False, max_per_page=50
            )
        except Exception as e:
            db.session.rollback()
            raise e

    #subqueries

    @staticmethod
    def query(filter_data, start, length ):
        try:
            from src import User

            subquery = db.session.query(
                Property.owner_id,
                func.avg(Property.living_area).label('avg_liv_area')
            ).filter(
                Property.status == Property.STATUSES.active
            ).group_by(
                Property.owner_id
            ).subquery()

            return db.session.query(
                User, subquery
            ).join(
                subquery,
                User.id == subquery.c.owner_id
            ).filter(
                filter_data,
            ).paginate(
                page=start, per_page=length, error_out=False,max_per_page=50)
        except Exception as e:
            db.session.rollback()
            raise e

    # @staticmethod
    # def query(filter_data, start, length):
    #     try:
    #         return db.session.query(
    #             Property.owner_id,
    #             Property.living_area,
    #             Property.price,
    #             func.datediff(text('days'),datetime.utcnow() - \
    #                           Property.created_at.label('timeDiff')
    #                           )
    #         ).filter(
    #             Property.status == Property.STATUSES.active
    #         ).paginate(
    #            page=start, per_page=length, error_out=False,max_per_page=256)
    #     except Exception as e:
    #         db.session.rollback()
    #         raise e

class StringValue(enum.Enum):
    def __repr__(self):
        return '%s.%s'%(self.__class__.__name__, self.name)


class PropertyStatus(StringValue):
    inactive = 'SOLD'
    active = 'AVAILABLE'

class Property(BaseModelMixin, ModelsMixin, db.Model):

    __tablename__ = "properties"
    query_class = PropertyQuery

    STATUSES = PropertyStatus

    id = sa.Column(UUID(as_uuid=True), default = uuid4, primary_key =True)
    address = sa.Column(sa.String(255), nullable = False)
    price = sa.Column(sa.Float(precision=2),nullable = False)
    living_area = sa.Column(sa.Float(precision=2), nullable = False)
    status = sa.Column(
        sa.Enum(
            PropertyStatus,
            name = 'ck_property_statuses',
            native_enum = False,
            create_constraint = True,
            length=255,
            validate_strings = True
        ),
        nullable = False,
        default = PropertyStatus.active,
        server_default = PropertyStatus.active.name
    )

    owner_id = db.Column(UUID(as_uuid=True),
                         db.ForeignKey('users.id', ondelete="RESTRICT"),
                         nullable = False,
                         index=True)

    owner = orm.relationship("User", back_populates="properties",
                             uselist=False
                             )

    sale = orm.relationship("Sale", back_populates="properties", uselist=False)



