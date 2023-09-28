from abc import ABC, abstractmethod #For abstract Methods
from trade_smart_backend.apps.strategy.app_settings import STRATEGY_EXECUTION_CONFIG
from trade_smart_backend.apps.strategy.async_functions import *
from trade_smart_backend.entities.indicator_entity import IndicatorEntity
import asyncio

class StrategyBase(ABC):
    def __init__(self, strategy_execution_entity=None, strategy_execution_config="config1"):
        self.execution_entity = strategy_execution_entity
        self.execution_config_json = STRATEGY_EXECUTION_CONFIG[strategy_execution_config]

    def prepare_data_for_strategy_execution(self):
        # prepare indicator entites using config.
        # call data prepare step for all entites above and pass it to respective child class

        indicator_requirements = self.execution_config_json.get("indicator_data", [])
        indicator_list = []
        for indicator_requirement in indicator_requirements:
            indicator_list.append(IndicatorEntity(indicator_requirement))
        indicator_list = [IndicatorEntity("Mohit"), IndicatorEntity("Divya"), IndicatorEntity("Parth")]
        for i in var:
            print(i.__dict__)
        x = asyncio.run(indicator_data_populator_bulk(*var))
        for i in var:
            print(i.__dict__)
        print("Hello")


# from trade_smart_backend.apps.strategy.strategy_base import StrategyBase
# StrategyBase().prepare_data_for_strategy_execution()