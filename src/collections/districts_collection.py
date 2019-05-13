import csv
from enum import Enum
import json
from pathlib import Path
import sys
import threading
from typing import Any, Callable, Dict, Generator, List

import attr
import ee

# allow higher size of CSV fields (because of the geometry field)
csv.field_size_limit(sys.maxsize)

BRATISLAVA_DISTRICTS = ["Bratislava I", "Bratislava II", "Bratislava III", "Bratislava IV", "Bratislava V"]
KOSICE_DISTRICTS = ["Košice I", "Košice II", "Košice III", "Košice IV", "Košice - okolie"]


class Land(Enum):
    Lowland = "lowland"
    Highland = "highland"


REGION_LAND_MAPPING = {
    "Bratislavský": Land.Lowland,
    "Trnavský": Land.Lowland,
    "Nitriansky": Land.Lowland,
    "Trenčiansky": Land.Highland,
    "Žilinský": Land.Highland,
    "Banskobystrický": Land.Highland,
    "Prešovský": Land.Highland,
    "Košický": Land.Lowland,
}


@attr.s(auto_attribs=True)
class District:
    district_name: str
    region_name: str
    area: float
    geometry: ee.Geometry
    land: Land


def combine_geometries(geometries: Generator[str, None, None]) -> ee.Geometry:
    united_geometry = ee.Geometry(json.loads(next(geometries)))
    for geo in geometries:
        united_geometry = united_geometry.union(ee.Geometry(json.loads(geo)))
    return united_geometry


class DistrictsCollection:
    regions: Dict[str, District] = {}

    def __init__(self, regions_file_path: Path):
        bratislava, kosice = [], []

        with regions_file_path.open(mode="r") as regions_file:
            for row in csv.DictReader(regions_file):
                if row["DistrictName"] in BRATISLAVA_DISTRICTS:
                    bratislava.append(row)
                elif row["DistrictName"] in KOSICE_DISTRICTS:
                    kosice.append(row)
                else:
                    self.regions[row["DistrictName"]] = District(
                        district_name=row["DistrictName"],
                        region_name=row["RegionName"],
                        area=float(row["Area"]),
                        geometry=ee.Geometry(json.loads(row["geometry"])),
                        land=REGION_LAND_MAPPING[row["RegionName"]],
                    )

        self.regions["Bratislava I-V"] = District(
            district_name="Bratislava I-V",
            region_name="Bratislavský",
            area=sum([float(r["Area"]) for r in bratislava]),
            geometry=combine_geometries(r["geometry"] for r in bratislava),
            land=Land.Lowland,
        )
        self.regions["Košice I-IV and Košice - okolie"] = District(
            district_name="Košice I-IV and Košice - okolie",
            region_name="Košický",
            area=sum([float(r["Area"]) for r in kosice]),
            geometry=combine_geometries(r["geometry"] for r in kosice),
            land=Land.Lowland,
        )

    def filter_districts(self, names: List[str]) -> "DistrictsCollection":
        if names is None:
            return self
        self.regions = {key: value for key, value in self.regions.items() if key in names}
        return self

    def iterate(self, func: Callable[[District, List[Any]], None]) -> List[Any]:
        return_value: List[Any] = []
        threads: List[threading.Thread] = []

        for region in self.regions.values():
            new_thread = threading.Thread(target=func, args=(region, return_value))
            new_thread.start()
            threads.append(new_thread)

        for running_thread in threads:
            running_thread.join()

        return return_value
