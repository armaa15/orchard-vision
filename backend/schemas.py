from pydantic import BaseModel


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