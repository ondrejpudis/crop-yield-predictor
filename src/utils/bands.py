from typing import List

import attr


@attr.s(auto_attribs=True)
class Bands:
    values: List[str]
    names: List[str]

    def add(self, **new_bands):
        for name, value in new_bands.items():
            self.values.append(value)
            self.names.append(name)
