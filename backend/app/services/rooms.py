from typing import Optional
from uuid import UUID

from app.core.roles import Role
from app.core.security import now_utc
from app.models import Membership, Room
from app.repositories.events import create_event, get_next_seq
from app.repositories.memberships import create_membership
from app.repositories.rooms import create_room


def create_room_service(db, name: str, principal_id: UUID) -> Room:
    room = create_room(db, name, principal_id)
    payload = f'{{"room_id":"{room.id}","name":"{name}"}}'
    seq = get_next_seq(db, room.id)
    create_event(db, room.id, "room.created", payload, actor_principal_id=principal_id, seq=seq)
    return room


def join_room_by_invite(db, token: bytes, principal_id: UUID) -> Optional[Membership]:
    from app.repositories.invites import get_invite_by_token, mark_invite_consumed
    invite = get_invite_by_token(db, token)
    if not invite or invite.revoked or invite.consumed:
        return None
    if invite.expires_at < now_utc():
        return None
    membership = create_membership(
        db, invite.room_id, principal_id, role=Role.WATCHER, is_host=False
    )
    mark_invite_consumed(db, invite.id, principal_id)
    payload = f'{{"room_id":"{invite.room_id}","principal_id":"{principal_id}"}}'
    seq = get_next_seq(db, invite.room_id)
    create_event(
        db, invite.room_id, "membership.joined", payload, actor_principal_id=principal_id, seq=seq
    )
    return membership
