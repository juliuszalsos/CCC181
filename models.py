from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    role: Mapped[str] = mapped_column(String(20), default="visitor", server_default="visitor")
    high_contrast: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")  # FR-09 Accessibility

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="user")

    __table_args__ = (
        CheckConstraint("role IN ('visitor', 'staff')", name="ck_users_role"),
    )


class Service(db.Model):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    avg_minutes: Mapped[int] = mapped_column(default=10, server_default="10")
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")  # FR-07 Service toggle

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="service")

    __table_args__ = (
        CheckConstraint("avg_minutes > 0", name="ck_services_avg_minutes"),
    )


class Ticket(db.Model):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(20), default="waiting", server_default="waiting")
    is_priority: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")  # FR-08 Priority lane
    copies_requested: Mapped[int] = mapped_column(default=1, server_default="1")  # FR-10 Copy count
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)  # FR-11 Staff note
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="tickets")
    service: Mapped["Service"] = relationship(back_populates="tickets")

    __table_args__ = (
        CheckConstraint(
            "status IN ('waiting', 'called', 'served', 'no-show', 'left', 'cancelled')",
            name="ck_tickets_status",
        ),
        CheckConstraint(
            "copies_requested BETWEEN 1 AND 5",
            name="ck_tickets_copies_requested",
        ),
    )