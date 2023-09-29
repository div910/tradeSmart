import logging
from sqlalchemy import create_engine, inspect, column
from sqlalchemy.orm import Session, joinedload, load_only
from django.conf import settings
from urllib.parse import quote


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SqlAlchemyEngine(object, metaclass=Singleton):

    def __init__(self, **kwargs):
        self.engines = {}
        self.database = kwargs.get('database', 'default')
        self.user = settings.DATABASES[self.database]["USER"]
        self.password = settings.DATABASES[self.database]["PASSWORD"]

    def get_connection(self):
        if self.database not in self.engines:
            engine = create_engine(
                f'mysql+pymysql://{self.user}:%s@{settings.DATABASES[self.database]["HOST"]}:{settings.DATABASES[self.database]["PORT"]}/{settings.DATABASES[self.database]["NAME"]}?charset=utf8mb4' % quote(
                    f'{self.password}'), pool_size=10, max_overflow=20, pool_pre_ping=True,
                pool_recycle=3600, connect_args={'read_timeout': 1200}
            )
            self.engines[self.database] = engine
        return self.engines[self.database]

def sql_alchemy_connect(database):
    engine = SqlAlchemyEngine(database=database).get_connection()
    return engine


def insert(engine, entity):
    """
        Function to insert a single row into table.
        parameters:
            table: Table class object
            entity: table entity to insert
        returns:
    """
    table = entity.__class__
    class_object = table(entity._asdict())
    with Session(engine) as session:
        session.begin()
        try:
            session.add(class_object)
        except Exception as ex:
            session.rollback()
            logging.error(f"error while inserting in table, Error: ", ex)
        else:
            session.commit()


def update(engine, table, filter_list, update_dict):
    """
        Function to update rows in table.
        parameters:
            table: table class name
            filter_list: list of dict of filters, format - [{"column": "col", "value": "val", "op": "=="}]
            update_dict: dict of {"column", "value"}
        returns:
    """
    with Session(engine) as session:
        session.begin()
        try:
            q = session.query(table)
            for filters in filter_list:
                q = add_filter(q, filters["value"], getattr(table, filters["column"]), filters["op"])
            update_filter_dict = {}
            for attr, value in update_dict.items():
                update_filter_dict.update({getattr(table, attr): value})
            q = q.update(update_filter_dict)
        except Exception as ex:
            session.rollback()
            logging.error(f"error while updating in table {str(table)}, Error: ", ex)
            raise ex
        else:
            session.commit()


def delete(engine, table, filter_list):
    """
        Function to delete rows in table.
        parameters:
            table: table class name
            filter_list: list of dict of filters, format - [{"column": "col", "value": "val", "op": "=="}]
        returns:
    """
    with Session(engine) as session:
        session.begin()
        try:
            q = session.query(table)
            for filters in filter_list:
                q = add_filter(q, filters["value"], getattr(table, filters["column"]), filters["op"])
            q = q.delete()
        except Exception as ex:
            session.rollback()
            logging.error(f"error while deleting in table {str(table)}, Error: ", ex)
            raise ex
        else:
            session.commit()


def fetch_one_row(engine, table, filter_list, return_type='entity'):
    """
        Function to fetch a single row from table.
        parameters:
            table: table class name
            filter_list: list of dict of filters, format - [{"column": "col", "value": "val", "op": "=="}]
        returns: Class object of table
    """
    with Session(engine) as session:
        session.begin()
        try:
            q = session.query(table)
            for filters in filter_list:
                q = add_filter(q, filters["value"], getattr(table, filters["column"]), filters["op"])
            result = q.first()
            if return_type == "dict":
                result = result._asdict()
            return result
        except Exception as ex:
            logging.error(f"error while fetching from table {str(table)}, Error: ", ex)
            return None


def fetch_rows(engine, table, filter_list, projections=[], return_type='dict'):
    """
        Function to fetch multiple rows from table.
        parameters:
            table: table class name
            filter_list: list of dict of filters, format - [{"column": "col", "value": "val", "op": "=="}]
        returns: List of class object of table
    """
    with Session(engine) as session:
        session.begin()
        try:
            q = session.query(table)
            for filters in filter_list:
                q = add_filter(q, filters["value"], getattr(table, filters["column"]), filters["op"])
            entity = q.all()
            if return_type == "dict":
                result = [x._asdict() for x in entity]
            else:
                result = entity
            return result
        except Exception as ex:
            logging.error(f"error while fetching from table {str(table)}, Error: ", ex)
            raise ex


def fetch_columns(engine, table, column_list, filter_list=[]):
    """
        Function to fetch specific columns from table.
        parameters:
            table: Table class name
            column_list: List of column names
            filter_list: List of dict of filters, format - [{"column": "col", "value": "val", "op": "=="}]
        returns: List of dict of result
    """
    with Session(engine) as session:
        session.begin()
        try:
            columns = [getattr(table, column) for column in column_list]
            q = session.query().with_entities(*columns)
            for filters in filter_list:
                q = add_filter(q, filters["value"], getattr(table, filters["column"]), filters["op"])
            entities = q.all()
            result = [x._asdict() for x in entities]
            return result
        except Exception as ex:
            logging.error(f"error while fetching from table {str(table)}, Error: ", ex)


def execute_query(engine, query: str):
    """
        Function to fetch specific columns from table.
        parameters:
            query: Mysql query to execute
        returns: List of Dict of result
    """
    with Session(engine) as session:
        session.begin()
        try:
            segment = session.execute(query)
            result = [x._asdict() for x in segment]
            session.commit()
            return result
        except Exception as ex:
            session.rollback()
            logging.error(f"error while executing query: {query}, Error: ", ex)


def add_filter(query, value, column, operator):
    if operator == "==":
        return query.filter(column == value)
    elif operator == "!=":
        return query.filter(column != value)
    elif operator == ">":
        return query.filter(column > value)
    elif operator == "<":
        return query.filter(column < value)
    elif operator == ">=":
        return query.filter(column >= value)
    elif operator == "<=":
        return query.filter(column <= value)
    elif operator.lower() == "in":
        # Value should be list of elements
        return query.filter(column.in_(value))
    elif operator.lower() == "not in":
        # Value should be list of elements
        return query.filter(column.not_in(value))
    elif operator.lower() == "between":
        # Value should be a list of two elements
        return query.filter(column.between(value[0], value[1]))
    elif operator.lower() == "like":
        return query.filter(column.like(value))
    elif operator.lower() == "orderbydesc":
        return query.order_by(column.desc())
    elif operator.lower() == "is":
        return query.filter(column.is_(value))


def crete_update_dict(object):
    """
        Function to create dict object for update query.
        parameters:
            object: object of table to be updated
        returns: Dict of result
    """
    dict = {}
    for c in inspect(object).mapper.column_attrs:
        if getattr(object, c.key) is not None:
            dict.update({c.key: getattr(object, c.key)})
    return dict


def create_dict_from_object(object):
    """
        Function to create dictionary from table object.
        parameters:
            object: object of table to be updated
        returns: Dict of result
    """
    return {c.key: getattr(object, c.key) for c in inspect(object).mapper.column_attrs}


def save_or_update(engine, table, entity):
    """
        Function to create a new entry or update old one, on basis of table's unique id.
        parameters:
            table: table name
            entity: table object to be inserted
    """
    class_object = table(entity._asdict())
    with Session(engine) as session:
        session.begin()
        try:
            q = session.query(table)
            q = add_filter(q, inspect(class_object).class_.unique_id, class_object.unique_id, "==")
            db_entity = q.first()
            if db_entity is None:
                session.add(class_object)
            else:
                dict = crete_update_dict(class_object)
                dict.pop("unique_id")
                if not dict:
                    return
                q = session.query(table)
                q = add_filter(q, inspect(class_object).class_.id, db_entity.id, "==")
                res = q.update(dict)
        except Exception as ex:
            session.rollback()
            logging.error("Error while saving or updating, Error: ", ex)
            raise ex
        else:
            session.commit()


def bulk_insert(engine, entity_list):
    with Session(engine) as session:
        session.begin()
        try:
            session.bulk_save_objects(entity_list)
        except Exception as ex:
            session.rollback()
            logging.error(f"error while inserting in table, Error: ", ex)
            raise ex
        else:
            session.commit()


def save(engine, table, entity):
    """
        Function to create a new entry .
        parameters:
            table: table name
            entity: table object to be inserted
    """
    with Session(engine) as session:
        session.begin()
        try:
            session.add(entity)
        except Exception as ex:
            session.rollback()
            logging.error("Error while saving or updating, Error: ", ex)
            raise ex
        else:
            session.commit()


def fetch_rows_limited(engine, table, filter_list, columns=[], relationships=[], limit=None):
    """
        Function to fetch multiple rows from table.
        parameters:
            table: table class name
            filter_list: list of dict of filters, format - [{"column": "col", "value": "val", "op": "=="}]
            columns: list of columns to be fetched , ["id","unique_id"]
            relationships: list of relationships to be fetched , ["tag_mapping.tag","url_mapping.url"]
            limit: no of rows to be fetched
        returns: List of class object of table
    """
    with Session(engine) as session:
        session.begin()
        try:
            q = session.query(table)
            for filters in filter_list:
                q = add_filter(q, filters["value"], getattr(table, filters["column"]), filters["op"])
            q = add_columns_projections(q, columns)
            q = add_relationshsip_projections(q, relationships)
            entity = q.limit(limit).all() if limit is not None else q.all()
            return entity
        except Exception as ex:
            logging.error(f"error while fetching from table, Error: ", ex)


def add_columns_projections(q, columns=[]):
    if len(columns) == 0:
        return q
    q = q.options(load_only(*columns))
    return q


def add_relationshsip_projections(q, relationships=[]):
    if len(relationships) == 0:
        return q
    for relationship in relationships:
        split_relation = relationship.split(".")
        joined = joinedload(split_relation[0])
        for split in split_relation[1:]:
            joined = joined.joinedload(split)
        q = q.options(joined)
    return q


def execute_write(engine, query, values):
    try:
        with engine.connect() as cursor:
            resp = cursor.execute(query, values)
            return {'last_row_id': resp.lastrowid, 'row_count': resp.rowcount}
    except Exception as e:
        logging.error({'error': 'mysql thrown exception while updating', 'exception': str(e), 'logkey': 'mysql_helper'})
        return {'exception': str(e)}


def fetch_all(engine, query, params=[]):
    try:
        with engine.connect() as cursor:
            resp = cursor.execute(query, params)
            desc = resp.cursor.description
            result = [dict(zip([col[0] for col in desc], row)) for row in resp.fetchall()]
            return result
    except Exception as e:
        logging.error({
            'error': 'mysql thrown exception while fetching dict one.', 'exception': e, 'logkey': 'mysql_helper'
        })
        return None


def save_or_update_merge(engine, entity):
    """
        Function to insert a single row into table.
        parameters:
            table: Table class object
            entity: table entity to insert
        returns:
    """
    with Session(engine) as session:
        session.begin()
        try:
            upd_entity = session.merge(entity)
        except Exception as ex:
            session.rollback()
            logging.error(f"error while inserting in table, Error: ", ex)
        else:
            session.commit()
            # entity = result
        dict = create_dict_from_object(upd_entity)
    return entity.__class__(dict)


def fetch_count(engine, table, filter_list):
    """
        Function to fetch count.
        parameters:
            table: table class name
            filter_list: list of dict of filters, format - [{"column": "col", "value": "val", "op": "=="}]
        returns: List of class object of table
    """
    with Session(engine) as session:
        session.begin()
        try:
            q = session.query(table)
            for filters in filter_list:
                q = add_filter(q, filters["value"], getattr(table, filters["column"]), filters["op"])
            count = q.count()
            return count
        except Exception as ex:
            logging.error(f"error while fetching from table {str(table)}, Error: ", ex)
            raise ex


def execute_update_query(engine, query):
    try:
        with engine.connect() as cursor:
            resp = cursor.execute(query)
            return {'success': True, 'last_row_id': resp.lastrowid, 'row_count': resp.rowcount}
    except Exception as e:
        logging.error({
            "error": e,
            "message": "error occurred while inserting data into mysql table",
            "logkey": "mysql_helper"
        })
        return {'success': False, 'exception': e}