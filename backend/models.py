from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Orchard(Base):
    __tablename__ = "orchards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trees = relationship("Tree", back_populates="orchard")


class Tree(Base):
    __tablename__ = "trees"

    id = Column(Integer, primary_key=True, index=True)
    orchard_id = Column(Integer, ForeignKey("orchards.id"), nullable=False)
    section = Column(String, nullable=False)
    row_number = Column(Integer, nullable=False)
    position_in_row = Column(Integer, nullable=False)
    variety = Column(String, nullable=True)
    planting_year = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="active")
    notes = Column(String, nullable=True)

    orchard = relationship("Orchard", back_populates="trees")
    observations = relationship("Observation", back_populates="tree")


class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    tree_id = Column(Integer, ForeignKey("trees.id"), nullable=False)
    observed_on = Column(Date, nullable=False)
    photo_path = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    predicted_disease = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tree = relationship("Tree", back_populates="observations")