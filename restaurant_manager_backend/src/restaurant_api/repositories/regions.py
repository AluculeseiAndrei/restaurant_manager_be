from restaurant_api.data.regions import REGIONS_DATA


class JsonRegionRepository:
    def counties(self) -> list[str]:
        return list(REGIONS_DATA)

    def cities(self, county: str) -> list[str]:
        return list(REGIONS_DATA.get(county, []))
