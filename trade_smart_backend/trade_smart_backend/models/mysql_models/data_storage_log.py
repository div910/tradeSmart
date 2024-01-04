from trade_smart_backend.models.mysql_models.base_model import *

class DataStorageLog_Table(Base, Orm_helper):
    __tablename__ = 'data_storage_log'
    id = Column('id', Integer, autoincrement=True, primary_key=True)
    ins_name = Column('ins_name', String)
    ins_source = Column('ins_source', String)
    ins_destination = Column('ins_destination', String)
    ins_meta = Column('ins_meta', String)
    creation_time = Column('creation_time', TIMESTAMP, default=datetime.datetime.now())

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

class DataStorageLog:

    def __init__(self, data={}):
        self.database = "default"
        self.table_name = "data_storage_log"
        self.table = DataStorageLog_Table
        self.engine = sql_alchemy_connect("default")

    def insert(self, data_storage_log_list={}):
        try:
            data_storage_log_obj = DataStorageLog_Table(data_storage_log_list)
            res = save(self.engine, self.table, data_storage_log_obj)
        except Exception as ex:
            return {"success": False, "message": str(ex)}
        return {"success": True, "result": res}
