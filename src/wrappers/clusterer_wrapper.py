from pathlib import Path
from typing import Callable, Dict

import attr

from ..collections import GeoPointCollection
from ..collections.districts_collection import Land
from ..models import Clusterer

TRAINING_BANDS = ["shortwave_infrared_1", "shortwave_infrared_2", "evi", "ndvi"]


@attr.s(auto_attribs=True)
class ClustererWrapper:
    """Handles creating and returning a clusterer for given year and land."""

    build_function: Callable[[int], Clusterer]
    lowland_highland_split: bool

    year_clusterers: Dict[int, Clusterer] = {}
    land_clusterers: Dict[int, Dict[Land, Clusterer]] = {}

    geo_points: GeoPointCollection = GeoPointCollection(Path("datasets/geo_data/clusterer_training_points.csv"))

    def get(self, year: int, district_land: Land) -> Clusterer:
        if not self.lowland_highland_split:
            return self._get_regular(year)
        else:
            return self._get_by_land(year, district_land)

    def _get_regular(self, year: int) -> Clusterer:
        """Get a clusterer based on the year.

        If a clusterer does not exist, create and train it and store for future use. This saves some time because we
        don't need to build the object all over again.
        """
        if year not in self.year_clusterers:
            self.year_clusterers[year] = self.build_function(year).train(self.geo_points.features(), TRAINING_BANDS)
        return self.year_clusterers[year]

    def _get_by_land(self, year: int, land: Land) -> Clusterer:
        """Get a clusterer based on the year and type of the land."""
        if year not in self.land_clusterers:
            self.land_clusterers[year] = {
                land: self.build_function(year).train(self.geo_points.features(land), TRAINING_BANDS)
            }
        elif land not in self.land_clusterers[year]:
            self.land_clusterers[year][land] = self.build_function(year).train(
                self.geo_points.features(land), TRAINING_BANDS
            )
        return self.land_clusterers[year][land]
