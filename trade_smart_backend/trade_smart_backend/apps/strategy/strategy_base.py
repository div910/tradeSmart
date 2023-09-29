from abc import ABC, abstractmethod #For abstract Methods
from trade_smart_backend.apps.strategy.app_settings import STRATEGY_EXECUTION_CONFIG
from trade_smart_backend.apps.strategy.async_functions import *
from trade_smart_backend.entities.measurement_entity import MeasurementEntity
import asyncio

class StrategyBase(ABC):

    def __init__(self, strategy_execution_entity=None, strategy_execution_config="config1"):
        self.security_entity_obj = strategy_execution_entity
        self.execution_config_json = STRATEGY_EXECUTION_CONFIG[strategy_execution_config]

    def prepare_data_for_strategy_execution(self):
        # prepare measurement entites using config.
        # call financial_data prepare step for all entites above and pass it to respective child class
        strategy_meta={}
        all_measurements = self.execution_config_json.get("measurement_data", [])
        # Set Timestamp + Measurement from measurement_requirements
        # Set Tags from security_entity_obj
        # set projections from Measurement mapping
        measurement_list = [] #List of tuples that would have both strategy execution entity and measurement
        for one_measurement in all_measurements:
            measurement_obj = MeasurementEntity(**one_measurement)
            measurement_obj.set_tags(self.security_entity_obj)
            measurement_list.append(measurement_obj)
        asyncio.run(measurement_data_populator_bulk(*measurement_list))
        self.init_strategy(measurement_list, strategy_meta)
        print("Hello")

    def init_strategy(self, measurement_list):
        pass



# from trade_smart_backend.apps.strategy.strategy_base import StrategyBase
# StrategyBase().prepare_data_for_strategy_execution()