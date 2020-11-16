from .internal import Base
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime


class TrainExecution(Base):
    @declared_attr
    def __tablename__(cls):
        return "train_execution"

    id = sa.Column(sa.Integer, primary_key=True)
    train_id = sa.Column(sa.Integer, sa.ForeignKey('train.id'), nullable=False, unique=False)
    start = sa.Column(sa.DateTime(), nullable=False)
    end = sa.Column(sa.DateTime(), nullable=True)
    results_hash = sa.Column(sa.String(), nullable=True)
