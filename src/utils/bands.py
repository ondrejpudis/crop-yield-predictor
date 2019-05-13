from typing import List

import attr


@attr.s(auto_attribs=True)
class Bands:
    """Stores the lists of bands and their mapped names."""

    values: List[str]
    names: List[str]


# Default band values and their word equivalents
BANDS = Bands(
    values=["B1", "B2", "B3", "B4", "B5", "B7", "B4_1", "nd"],
    names=["blue", "green", "red", "near_infrared", "shortwave_infrared_1", "shortwave_infrared_2", "evi", "ndvi"],
)
