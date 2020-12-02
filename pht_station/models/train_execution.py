import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from datetime import datetime

Base = declarative_base()


class TrainExecution(Base):
    __tablename__ = "train"

    id = sa.Column(sa.Integer, primary_key=True)
    train_id = sa.Column(sa.Integer, sa.ForeignKey('train.id'), nullable=False, unique=False)
    start = sa.Column(sa.DateTime(), nullable=False)
    end = sa.Column(sa.DateTime(), nullable=True)
    results_hash = sa.Column(sa.String(), nullable=True)
