from __future__ import annotations
import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase

class University(AuditableBase):
    """
    Top-level organizational entity representing a University system.
    """
    __tablename__ = "universities"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    campuses: Mapped[List["Campus"]] = relationship("Campus", back_populates="university", cascade="all, delete-orphan")

class Campus(AuditableBase):
    """
    Represents a specific physical location or campus.
    """
    __tablename__ = "campuses"

    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    university_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)

    university: Mapped["University"] = relationship("University", back_populates="campuses")
    buildings: Mapped[List["Building"]] = relationship("Building", back_populates="campus", cascade="all, delete-orphan")

class Faculty(AuditableBase):
    """
    Academic Faculty or division within the university.
    """
    __tablename__ = "faculties"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)

    departments: Mapped[List["Department"]] = relationship("Department", back_populates="faculty", cascade="all, delete-orphan")

class Department(AuditableBase):
    """
    Represents functional/academic departments managing assets.
    """
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    faculty_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("faculties.id", ondelete="SET NULL"), nullable=True)

    faculty: Mapped[Optional["Faculty"]] = relationship("Faculty", back_populates="departments")
    users: Mapped[List["User"]] = relationship("User", back_populates="department")
    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="department")
    budgets: Mapped[List["DepartmentBudget"]] = relationship("DepartmentBudget", back_populates="department", cascade="all, delete-orphan")
    work_orders: Mapped[List["WorkOrder"]] = relationship("WorkOrder", back_populates="department")

class Building(AuditableBase):
    """
    Physical structure located on a Campus.
    """
    __tablename__ = "buildings"

    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    campus_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campuses.id", ondelete="CASCADE"), nullable=False)

    campus: Mapped["Campus"] = relationship("Campus", back_populates="buildings")
    floors: Mapped[List["Floor"]] = relationship("Floor", back_populates="building", cascade="all, delete-orphan")

class Floor(AuditableBase):
    """
    A specific floor level within a Building.
    """
    __tablename__ = "floors"

    level: Mapped[int] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)

    building: Mapped["Building"] = relationship("Building", back_populates="floors")
    rooms: Mapped[List["Room"]] = relationship("Room", back_populates="floor", cascade="all, delete-orphan")

class Room(AuditableBase):
    """
    A designated room or area on a Floor.
    """
    __tablename__ = "rooms"

    number: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. Lab, Lecture Hall, Office
    floor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("floors.id", ondelete="CASCADE"), nullable=False)

    floor: Mapped["Floor"] = relationship("Floor", back_populates="rooms")
    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="room")
