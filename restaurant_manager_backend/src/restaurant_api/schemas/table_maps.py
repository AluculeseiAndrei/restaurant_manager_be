from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


ElementKind = Literal["table", "bar", "booth", "stage", "wall", "service_area", "decoration"]
TableStatus = Literal["available", "occupied", "reserved", "unavailable"]


class FloorPlanElement(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    kind: ElementKind
    label: str | None = Field(default=None, max_length=80)
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(gt=0, le=10000)
    height: float = Field(gt=0, le=10000)
    rotation: float = Field(default=0, ge=0, lt=360)
    z_index: int = Field(default=0, alias="zIndex")
    table_id: str | None = Field(default=None, alias="tableId")
    capacity: int | None = Field(default=None, ge=1, le=100)
    status: TableStatus | None = None
    model_config = {"populate_by_name": True}


class FloorPlanUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    width: float = Field(gt=0, le=10000)
    height: float = Field(gt=0, le=10000)
    grid_size: int = Field(default=40, alias="gridSize", ge=1, le=200)
    snap_to_grid: bool = Field(default=True, alias="snapToGrid")
    elements: list[FloorPlanElement] = Field(default_factory=list)
    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_layout(self):
        ids = [str(element.id) for element in self.elements]
        if len(ids) != len(set(ids)):
            raise ValueError("Floor-plan element IDs must be unique")
        table_ids = [element.table_id for element in self.elements if element.kind == "table" and element.table_id]
        if len(table_ids) != len(set(table_ids)):
            raise ValueError("A restaurant table can only appear once on the floor plan")
        for element in self.elements:
            if element.x + element.width > self.width or element.y + element.height > self.height:
                raise ValueError(f"Element '{element.label or element.kind}' is outside the floor plan")
        furniture = [element for element in self.elements if element.kind in {"table", "booth", "bar"}]
        for index, first in enumerate(furniture):
            for second in furniture[index + 1:]:
                if _overlaps(first, second):
                    raise ValueError(f"Elements '{first.label or first.kind}' and '{second.label or second.kind}' overlap")
        return self


def _overlaps(first: FloorPlanElement, second: FloorPlanElement) -> bool:
    return not (first.x + first.width <= second.x or second.x + second.width <= first.x
                or first.y + first.height <= second.y or second.y + second.height <= first.y)


class FloorPlanResponse(FloorPlanUpdate):
    id: str
    restaurant_id: str = Field(alias="restaurantId")
    version: int
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
