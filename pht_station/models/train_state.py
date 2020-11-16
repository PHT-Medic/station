from .internal import Base
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime


class TrainState(Base):
    @declared_attr
    def __tablename__(cls):
        return "train_state"
    id = sa.Column(sa.Integer, primary_key=True)
    state = sa.Column(sa.String(), nullable=True)
