import contextlib
import functools
import logging

from airflow.hooks.base_hook import BaseHook
import sqlalchemy.orm


@contextlib.contextmanager
def open_session():
    session = None
    try:
        conn = BaseHook.get_connection('pht_station_all_postgres_station_db')
        engine = sqlalchemy.create_engine(
            f'postgresql+psycopg2://{conn.login}:{conn.password}@{conn.host}/{conn.schema}')
        session = sqlalchemy.orm.Session(bind=engine)
        yield session
        session.commit()
    except Exception as e:
        logging.warning(f'The following exception occurred while a database session was open: {e}!')
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()


def provide_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        arg_session = 'session'

        func_params = func.__code__.co_varnames
        session_in_args = arg_session in func_params and \
            func_params.index(arg_session) < len(args)
        session_in_kwargs = arg_session in kwargs

        if session_in_kwargs or session_in_args:
            return func(*args, **kwargs)
        else:
            with open_session() as session:
                kwargs[arg_session] = session
                return func(*args, **kwargs)
    return wrapper
