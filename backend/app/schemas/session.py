from pydantic import BaseModel


class SessionCreate(BaseModel):
    display_name: str


class SessionView(BaseModel):
    session_id: str
    principal_id: str
    display_name: str
    expires_at: str
    csrf_token: str
