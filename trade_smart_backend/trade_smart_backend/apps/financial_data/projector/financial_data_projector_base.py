from abc import ABC, abstractmethod #For abstract Methods
from trade_smart_backend.utils.influx_db_utils import Influx
import asyncio

class DataProjector(ABC):

    def __init__(self, data_collector_entity=None):
        self.security_entity_obj = data_collector_entity
        self.symbol = self.security_entity_obj.symbol