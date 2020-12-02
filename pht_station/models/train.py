import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from datetime import datetime

Base = declarative_base()


class Train(Base):
    __tablename__ = "train"

    id = sa.Column(sa.Integer, primary_key=True)
    train_id = sa.Column(sa.String(200), unique=True, nullable=False)
    created_at = sa.Column(sa.DateTime(), default=datetime.now(), nullable=False)
    modified_at = sa.Column(sa.DateTime(), nullable=True)
    last_execution = sa.Column(sa.DateTime(), nullable=True)
    train_hash = sa.Column(sa.String(), nullable=False)
    creator = sa.Column(sa.String(), nullable=False)
    creator_mail = sa.Column(sa.String(), nullable=True)
    active = sa.Column(sa.Boolean(), default=False, nullable=False)
    run_args = sa.Column(sa.String(), nullable=False)
    state = sa.Column(sa.Integer, sa.ForeignKey('train_state.id'), nullable=True)
