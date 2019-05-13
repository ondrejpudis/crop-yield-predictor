"""Convert an XML geometry to GeoJSON."""

import csv
import json
from pathlib import Path
import sys

from lxml import etree

csv.field_size_limit(sys.maxsize)

with open(Path("region_borders_parsed.csv"), "w") as destination:
    with open(Path("region_borders.csv"), "r") as source:
        source_dict = csv.DictReader(source)
        destination_dict = csv.DictWriter(destination, fieldnames=source_dict.fieldnames)
        destination_dict.writeheader()
        for r in source_dict:
            coordinates = (
                etree.fromstring(r["geometry"]).xpath("/Polygon/outerBoundaryIs/LinearRing/coordinates")[0].text
            )
            r["geometry"] = json.dumps(
                {
                    "type": "Polygon",
                    "coordinates": [
                        list(reversed([[float(c) for c in pair.split(",")] for pair in coordinates.split(" ")]))
                    ],
                }
            )
            destination_dict.writerow(r)
