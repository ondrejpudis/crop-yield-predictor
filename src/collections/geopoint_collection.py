import csv
import json
from typing import Dict, List, Tuple

from ee import Feature, FeatureCollection

from .regions_collection import Land


class GeoPointCollection:
    feature_dict: Dict[str, List[Feature]] = {Land.Lowland.value: [], Land.Highland.value: []}

    def __init__(self, source_file_name: str):
        with open(source_file_name, "r") as source_file:
            [self.feature_dict[r["land"]].append(Feature(*self._process_row(r))) for r in csv.DictReader(source_file)]

    @staticmethod
    def _process_row(row: dict) -> Tuple:
        return json.loads(row[".geo"]), {"type": row["type"]}

    def features(self, land: Land = None) -> FeatureCollection:
        if land:
            return FeatureCollection(self.feature_dict[land.value])
        return FeatureCollection([*self.feature_dict[Land.Lowland.value], *self.feature_dict[Land.Highland.value]])
