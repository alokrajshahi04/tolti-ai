from pydantic import BaseModel


class InviteCreateResponse(BaseModel):
    invite_id: str
    token: str
    expires_at: str


class InviteView(BaseModel):
    invite_id: str
    expires_at: str
    consumed: bool
    revoked: bool
