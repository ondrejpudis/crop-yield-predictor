import csv
from enum import Enum
import json
import sys
import threading
from typing import Callable, Dict, List

import attr
import ee

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
class Region:
    district_name: str
    region_name: str
    area: float
    geometry: ee.Geometry
    land: Land


def combine_geometries(geometries):
    united_geometry = ee.Geometry(json.loads(next(geometries)))
    for geo in geometries:
        united_geometry = united_geometry.union(ee.Geometry(json.loads(geo)))
    return united_geometry


class RegionsCollection:
    regions: Dict[str, Region] = {}

    def __init__(self, regions_file_path):
        bratislava, kosice = [], []
        with open(regions_file_path, "r") as regions_file:
            for r in csv.DictReader(regions_file):
                if r["DistrictName"] in BRATISLAVA_DISTRICTS:
                    bratislava.append(r)
                elif r["DistrictName"] in KOSICE_DISTRICTS:
                    kosice.append(r)
                else:
                    self.regions[r["DistrictName"]] = Region(
                        district_name=r["DistrictName"],
                        region_name=r["RegionName"],
                        area=float(r["Area"]),
                        geometry=ee.Geometry(json.loads(r["geometry"])),
                        land=REGION_LAND_MAPPING[r["RegionName"]],
                    )
        self.regions["Bratislava I-V"] = Region(
            district_name="Bratislava I-V",
            region_name="Bratislavský",
            area=sum([float(r["Area"]) for r in bratislava]),
            geometry=combine_geometries(r["geometry"] for r in bratislava),
            land=Land.Lowland,
        )
        self.regions["Košice I-IV and Košice - okolie"] = Region(
            district_name="Košice I-IV and Košice - okolie",
            region_name="Košický",
            area=sum([float(r["Area"]) for r in kosice]),
            geometry=combine_geometries(r["geometry"] for r in kosice),
            land=Land.Lowland,
        )

    def filter_districts(self, names: List) -> "RegionsCollection":
        if names is None:
            return self
        self.regions = {key: value for key, value in self.regions.items() if key in names}
        return self

    def iterate(self, func: Callable) -> List:
        return_value, threads = [], []
        for region in self.regions.values():
            t = threading.Thread(target=func, args=(region, return_value))
            t.start()
            threads.append(t)
        [t.join() for t in threads]
        return return_value
