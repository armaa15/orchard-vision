from pydantic import BaseModel
from datetime import date, datetime


class TreeCreate(BaseModel):
    orchard_id: int
    section: str
    row_number: int
    position_in_row: int
    variety: str | None = None
    planting_year: int | None = None
    notes: str | None = None


class TreeRead(BaseModel):
    id: int
    orchard_id: int
    section: str
    row_number: int
    position_in_row: int
    variety: str | None
    planting_year: int | None
    status: str
    notes: str | None

    model_config = {"from_attributes": True}

class ObservationCreate(BaseModel):
    tree_id: int
    observed_on: date
    notes: str | None = None

class ObservationRead(BaseModel):
    id: int
    tree_id: int
    observed_on: date
    notes: str | None
    created_at: datetime
    photo_path: str | None
    predicted_disease: str | None
    confidence: float | None

    model_config = {"from_attributes": True}
