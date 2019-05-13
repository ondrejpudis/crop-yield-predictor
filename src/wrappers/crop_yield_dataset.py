import csv
from pathlib import Path
import re
from typing import Dict, List, Optional

import ee
from sklearn.model_selection import train_test_split

from ..collections import District
from .clusterer_wrapper import ClustererWrapper

DISTRICT_REGEX = re.compile("^District of (?P<district_name>.+)")


def safe_float(value: float) -> Optional[float]:
    try:
        return float(value)
    except ValueError:
        return None


class CropYieldDataset:
    """A wrapper for creating training and testing data for prediction model."""

    training_years: List[int]
    testing_years: List[int]
    clusterer: ClustererWrapper
    crop_yield_data: Dict[str, Dict[int, Optional[float]]] = {}

    def __init__(self, years: List[int], clusterer: ClustererWrapper, crop_data_path: Path):
        """Initialise the instance.

        Split provided list of years into training and testing years (testing years are 25%). Read the past crop yields
        data.
        """
        self.training_years, self.testing_years = train_test_split(years, random_state=1)
        self.clusterer = clusterer

        self._read_dataset(crop_data_path, years)

    def _read_dataset(self, path: Path, years: List[int]):
        with path.open(mode="r") as crop_data_source:
            for row in csv.DictReader(crop_data_source, delimiter=";"):
                try:
                    district_name = DISTRICT_REGEX.findall(row["district"])[0]
                    self.crop_yield_data[district_name] = {y: safe_float(row[str(y)]) for y in years}
                except IndexError:
                    continue

    def _build_feature_collection(self, years: List[int], district: District, bands: List) -> ee.FeatureCollection:
        """Create a collection of associations of aggregated remote sensing data and crop yield value."""
        features = []

        for y in years:
            fields_in_year = self.clusterer.get(y, district.land).cluster(district.geometry, scale=500)
            data = {band: fields_in_year.aggregate_mean(property=band) for band in bands}

            if self.crop_yield_data[district.district_name][y] is not None:
                data["yield_value"] = self.crop_yield_data[district.district_name][y]
                features.append(ee.Feature(None, data))

        return ee.FeatureCollection(features)

    def training_data(self, district: District, bands: List) -> ee.FeatureCollection:
        return self._build_feature_collection(self.training_years, district, bands)

    def testing_data(self, district: District, bands: List) -> ee.FeatureCollection:
        return self._build_feature_collection(self.testing_years, district, bands)


class PredictionCropYieldDataset(CropYieldDataset):
    """A prediction model data builder in prediction mode."""

    testing_year: int

    def __init__(self, years: List[int], clusterer: ClustererWrapper, crop_data_path: Path):
        """Initialise the instance without calling parent.

        Assign all the years except for the last as training, last year is a year for prediction."""
        self.training_years, self.testing_year = years[:-1], years[-1]
        self.clusterer = clusterer

        self._read_dataset(crop_data_path, self.training_years)

    def testing_data(self, district: District, bands: List) -> ee.FeatureCollection:
        """Aggregate the remote sensing data for the one year.

        No yield value is appended because in the prediction mode, we expect that there is no such value known."""
        fields_in_year = self.clusterer.get(self.testing_year, district.land).cluster(district.geometry, scale=500)
        data = {band: fields_in_year.aggregate_mean(property=band) for band in bands}

        return ee.FeatureCollection(ee.Feature(None, data))
