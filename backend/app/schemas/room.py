from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str


class RoomView(BaseModel):
    id: str
    name: str
    host_principal_id: str
    driver_principal_id: str
    revision: int
    last_seq: int | None = None
