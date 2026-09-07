from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Principal(Base):
    __tablename__ = "principals"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    display_name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="principal", cascade="all, delete-orphan"
    )
    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="principal", cascade="all, delete-orphan"
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    principal_id: Mapped[UUID] = mapped_column(ForeignKey("principals.id"), nullable=False)
    session_token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    csrf_token: Mapped[str] = mapped_column(String(32), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    last_used_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    principal: Mapped[Principal] = relationship(back_populates="sessions")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200))
    host_principal_id: Mapped[UUID] = mapped_column(nullable=False)
    driver_principal_id: Mapped[UUID] = mapped_column(nullable=False)
    revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_seq: Mapped[Optional[int]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )
    invites: Mapped[list["Invite"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )
    events: Mapped[list["RoomEvent"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )


class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    principal_id: Mapped[UUID] = mapped_column(ForeignKey("principals.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_host: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(default=func.now())

    room: Mapped[Room] = relationship(back_populates="memberships")
    principal: Mapped[Principal] = relationship(back_populates="memberships")

    __table_args__ = (UniqueConstraint("room_id", "principal_id", name="uq_membership"),)


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by_principal_id: Mapped[UUID] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    consumed_by_principal_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    room: Mapped[Room] = relationship(back_populates="invites")


class RoomEvent(Base):
    __tablename__ = "room_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    seq: Mapped[Optional[int]] = mapped_column(nullable=True)
    schema_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    type: Mapped[str] = mapped_column(String(80), nullable=False)
    actor_principal_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    payload: Mapped[str] = mapped_column(String(2000), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(default=func.now())

    room: Mapped[Room] = relationship(back_populates="events")

    __table_args__ = (UniqueConstraint("room_id", "seq", name="uq_room_event_seq"),)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(64), nullable=False)
    principal_id: Mapped[UUID] = mapped_column(nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(200), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    result_reference: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (UniqueConstraint("key", name="uq_idempotency_key"),)
