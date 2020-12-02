import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class TrainState(Base):
    __tablename__ = "train_state"
    id = sa.Column(sa.Integer, primary_key=True)
    state = sa.Column(sa.String(), nullable=True)
