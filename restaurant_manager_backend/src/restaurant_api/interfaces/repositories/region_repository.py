from typing import Protocol


class RegionRepository(Protocol):
    def counties(self) -> list[str]: ...

    def cities(self, county: str) -> list[str]: ...
