from uuid import uuid4

from sqlalchemy import orm

from src import db
from src.models.common import BaseModelMixin, ModelsMixin
from sqlalchemy.dialects.postgresql import UUID


import sqlalchemy as sa

class SalesQuery(BaseModelMixin, db.Query):

    def get_one(self, _id):
        try:
            return self.filter(
                Sale.id == _id
            ).first()
        except Exception as e:
            db.session.rollback()

            raise e
    @staticmethod
    def get_all_sales(filter_data, start, length):
        try:
            from src import User

            return db.session.query(
                Sale
            ).join(
                User,
                Sale.buyer_id == User.id
            ).filter(
                filter_data
            ).paginate(
                page=start,per_page=length, error_out=False, max_per_page=50
            )
        except Exception as e:
            db.session.rollback()
            raise e


class Sale(BaseModelMixin, ModelsMixin, db.Model):

    __tablename__ = 'sales'
    query_class = SalesQuery

    id = sa.Column(UUID(as_uuid=True),
                               default = uuid4,
                               primary_key=True)


    buyer_id = db.Column(UUID(as_uuid=True),
                         db.ForeignKey('users.id', ondelete="RESTRICT"),
                         nullable = False,
                         index = True
                         )

    property_id = db.Column(UUID(as_uuid=True),
                            db.ForeignKey('properties.id', ondelete='RESTRICT'),
                            nullable = False,
                            index = True
                            )

    user = orm.relationship("User", back_populates='sale', uselist=False)

    properties = orm.relationship("Property",
                                  back_populates="sale", uselist=False)