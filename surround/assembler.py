# assembler.py
#
# Manages a set of stages and the data that is passed between them.
import sys
import os
import logging

from abc import ABC
from datetime import datetime

from .config import Config
from .visualiser import Visualiser
from .stage import Filter, Estimator

LOGGER = logging.getLogger(__name__)

class Assembler(ABC):

    # pylint: disable=too-many-instance-attributes
    def __init__(self, assembler_name="", validator=None, estimator=None, config=None):
        self.assembler_name = assembler_name
        self.config = config
        self.estimator = estimator
        self.validator = validator
        self.pre_filters = None
        self.post_filters = None
        self.visualiser = None

    def init_assembler(self, surround_data=None):
        if surround_data:
            self.surround_data = surround_data
        try:
            if self.pre_filters:
                for pre_filter in self.pre_filters:
                    pre_filter.init_stage(self.config)

            self.estimator.init_stage(self.config)

            if self.post_filters:
                for post_filter in self.post_filters:
                    post_filter.init_stage(self.config)
        except Exception:
            LOGGER.exception("Failed initiating Assembler")

    def run(self, surround_data=None):
        LOGGER.info("Starting '%s'", self.assembler_name)
        if surround_data:
            self.surround_data = surround_data
        try:
            self.validator.validate(self.surround_data, self.config)
            self.__run_pipeline()
        except Exception:
            LOGGER.exception("Failed running Assembler")

    def __run_pipeline(self):
        if self.pre_filters:
            self.execute_filters(self.pre_filters, self.surround_data)

        self.execute_main(self.surround_data)

        if self.post_filters:
            self.execute_filters(self.post_filters, self.surround_data)

    def execute_filters(self, filters, surround_data):
        surround_data.freeze()
        start_time = datetime.now()

        try:
            for stage in filters:
                self.execute_filter(stage, surround_data)
                if surround_data.errors:
                    LOGGER.error("Error during processing")
                    LOGGER.error(surround_data.errors)
                    break
            execution_time = datetime.now() - start_time
            surround_data.execution_time = str(execution_time)
            LOGGER.info("Filter took %s secs", execution_time)
        except Exception:
            LOGGER.exception("Failed processing Surround Filters")

        surround_data.thaw()

    def execute_filter(self, stage, stage_data):
        stage_start = datetime.now()
        stage.operate(stage_data, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            stage.dump_output(stage_data, self.config)

        # Calculate and log filter duration
        stage_execution_time = datetime.now() - stage_start
        stage_data.stage_metadata.append({type(stage).__name__: str(stage_execution_time)})
        LOGGER.info("Filter %s took %s secs", type(stage).__name__, stage_execution_time)

    def execute_main(self, surround_data):
        main_start = datetime.now()
        self.estimator.estimate(surround_data, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            self.estimator.dump_output(surround_data, self.config)

        # Calculate and log filter duration
        main_execution_time = datetime.now() - main_start
        surround_data.stage_metadata.append({type(self.estimator).__name__: str(main_execution_time)})
        LOGGER.info("Estimator %s took %s secs", type(self.estimator).__name__, main_execution_time)

    def load_config(self, module):
        if module:
            # Module already imported and has a file attribute
            mod = sys.modules.get(module)
            if mod and hasattr(mod, '__file__'):
                package_path = os.path.dirname(os.path.abspath(mod.__file__))
                root_path = os.path.dirname(package_path)
            else:
                raise ValueError("Invalid Python module %s" % module)

            self.set_config(Config(root_path))


            if not os.path.exists(self.config["output_path"]):
                os.makedirs(self.config["output_path"])
        else:
            self.set_config(Config())

    def set_config(self, config):
        if not config or not isinstance(config, Config):
            raise TypeError("config should be of class Config")
        self.config = config

    def set_estimator(self, estimator=None, pre_filters=None, post_filters=None):
        # Estimator is required
        if estimator is None:
            raise ValueError("estimator is not provided")
        if not isinstance(estimator, Estimator):
            raise TypeError("estimator should be of class Estimator")
        self.estimator = estimator

        if pre_filters:
            for pre_filter in pre_filters:
                if not isinstance(pre_filter, Filter):
                    raise TypeError("Prefilter should be of class Filter")
        self.pre_filters = pre_filters

        if post_filters:
            for post_filter in post_filters:
                if not isinstance(post_filter, Filter):
                    raise TypeError("post_filter should be of class Filter")
        self.post_filters = post_filters

    def set_visualiser(self, visualiser):
        # visualiser must be a type of Visualiser
        if visualiser and not isinstance(visualiser, Visualiser):
            raise TypeError("visualiser should be of class Visualiser")
        self.visualiser = visualiser
