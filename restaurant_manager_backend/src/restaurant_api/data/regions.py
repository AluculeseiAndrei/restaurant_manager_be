import json
from pathlib import Path


def _load_regions() -> dict[str, list[str]]:
    path = Path(__file__).parents[3] / "Utils" / "Region" / "corrected_regions.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as file:
        return json.load(file)


REGIONS_DATA = _load_regions()
