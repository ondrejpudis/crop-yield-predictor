from typing import List

import attr


@attr.s
class Bands:
    values: List[str] = attr.ib()
    names: List[str] = attr.ib()

    def add(self, **new_bands):
        for name, value in new_bands.items():
            self.values.append(value)
            self.names.append(name)
