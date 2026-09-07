from pydantic import BaseModel


class Snapshot(BaseModel):
    room: dict
    memberships: list[dict]
    active_run: dict | None
    snapshot_seq: int | None
    capabilities: dict
