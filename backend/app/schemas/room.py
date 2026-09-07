from pydantic import BaseModel


class RoomShell(BaseModel):
    id: str
    name: str = "Demo room"
    status: str = "ok"
