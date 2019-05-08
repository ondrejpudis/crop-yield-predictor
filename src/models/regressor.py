from functools import wraps
from typing import List

import ee

from ..collections import District
from ..utils.logger.console_logger import LOGGER
from ..utils.retry import retry_api_call


def log(func):
    @wraps(func)
    def inner(*args, **kwargs):
        LOGGER.info(f"START, server computation, {args[0].district_name}")
        result = func(*args, **kwargs)
        LOGGER.info(f"STOP, server computation, {args[0].district_name}")
        return result

    return inner


def district_predictor(model, args, yield_data, bands):
    @log
    @retry_api_call(n_times=3)
    def predict_per_district(element: District, return_value: List):
        model_instance = Regressor(model, bands, **args)
        model_instance.train(yield_data.training_data(element, bands.names))
        result = model_instance.classify(yield_data.testing_data(element, bands.names)).getInfo()
        result["district"] = element.district_name
        return_value.append(result)

    return predict_per_district


class Regressor:
    regressor: ee.Classifier

    def __init__(self, model, bands, **kwargs):
        self.bands = bands
        self.regressor = model(**kwargs).setOutputMode("REGRESSION")

    def train(self, dataset: ee.FeatureCollection):
        self.regressor = self.regressor.train(
            features=dataset, classProperty="yield_value", inputProperties=self.bands.names
        )

    def classify(self, dataset: ee.FeatureCollection) -> ee.FeatureCollection:
        return dataset.classify(self.regressor)
