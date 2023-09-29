from trade_smart_backend.models.mysql_models.base_model import *

class Security_Table(Base, Orm_helper):
    __tablename__ = 'security'
    id = Column('id', Integer, autoincrement=True, primary_key=True)
    name = Column('name', String)
    code = Column('code', String)
    creation_date = Column('ct', TIMESTAMP, default=datetime.datetime.now())

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

class Security:

    def __init__(self, data={}):
        self.database = "default"
        self.table_name = "security"
        self.table = Security_Table
        self.engine = sql_alchemy_connect("default")


    def get_security(self):
        filter_list = [
            {"column": 'name', 'value':'axis', 'op': '=='}
        ]
        res = fetch_rows(self.engine, self.table, filter_list)
        print(res)