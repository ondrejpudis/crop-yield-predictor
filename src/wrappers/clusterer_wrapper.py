from pathlib import Path
from typing import Callable, Dict, Union

from ..collections import GeoPointCollection
from ..collections.regions_collection import Land
from ..models import Clusterer

TRAINING_BANDS = ["shortwave_infrared_1", "shortwave_infrared_2", "evi", "ndvi"]


class ClustererWrapper:
    build_function: Callable[[int], Clusterer]
    use_split: bool
    computed_clusterers: Dict[int, Union[Dict[Land, Clusterer], Clusterer]] = {}

    def __init__(self, build_clusterer_function: Callable[[int], Clusterer], lowland_highland_split: bool):
        self.build_function = build_clusterer_function
        self.use_split = lowland_highland_split
        self.geo_points = GeoPointCollection(Path("datasets/geo_data/clusterer_training_points.csv"))

    def get(self, year: int, district_land: Land) -> Clusterer:
        if not self.use_split:
            return self._get_regular(year)
        else:
            return self._get_by_land(year, district_land)

    def _get_regular(self, year: int) -> Clusterer:
        if year not in self.computed_clusterers:
            self.computed_clusterers[year] = self.build_function(year).train(self.geo_points.features(), TRAINING_BANDS)
        return self.computed_clusterers[year]

    def _get_by_land(self, year: int, land: Land) -> Clusterer:
        if year not in self.computed_clusterers:
            self.computed_clusterers[year] = {
                land: self.build_function(year).train(self.geo_points.features(land), TRAINING_BANDS)
            }
        elif land not in self.computed_clusterers[year]:
            self.computed_clusterers[year][land] = self.build_function(year).train(
                self.geo_points.features(land), TRAINING_BANDS
            )
        return self.computed_clusterers[year][land]
