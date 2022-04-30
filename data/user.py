from flask_login import UserMixin
import sqlalchemy

from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    teleg_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    spisok = sqlalchemy.Column(sqlalchemy.String,  nullable=True)
    coordinates_shop = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    shopping_list = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f'<User> {self.id} {self.teleg_id} {self.address}'
